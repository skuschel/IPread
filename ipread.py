#!/usr/bin/env python

'''
Module providing the IPreader class for reading Image Plates data files.
Multiple Files can be combined to one single Image. Automatic PSL
conversion is applied.

Author: Stephan Kuschel
'''


from __future__ import absolute_import, division, print_function
import os
import warnings
import glob
import copy
import numpy as np
import numexpr as ne


__all__ = ['Infreader', 'IPreader', 'cnttopsl', 'readimg']
__version__ = '0.2.0'


# ----- Functions -----
def cnttopsl(cnt, R, S, L):
    '''
    converts a count number cnt to PSL using the given values for R,S, L.
    numexpr is used for calculations.
    '''
    return ne.evaluate('(R / 100.) ** 2 * (4000. / S) * '
                       '10.**(L * (cnt / 65536.0 - 0.5))')


def readimg(filename, rows, cols):
    '''
    Attempts to read the .img file filename (with or without '.img')
    assuming it was read with rows rows and cols cols.
    '''
    import numpy as np
    dt = np.dtype(np.uint16)
    dt = dt.newbyteorder('>')  # change to big endian
    filename.strip('.img')
    with open(filename + '.img', 'rb') as f:
        ret = np.reshape(np.fromfile(f, dtype=dt), (rows, cols))
    return np.array(ret, dtype=np.float64)


# ----- Classes -----
class Infreader(object):
    '''
    This class reads a single .inf file and provides informations about
    the read out settings used.
    Since the read out settings define the PSL conversion, it also
    defines a function to calculate
    the PSL value for a given number of counts at these readout settings.

    filename must be the exact filename of the .inf file _including_ its
    extension.
    '''

    def __init__(self, filename):
        self.filename = filename
        self.name = os.path.basename(filename.strip('\n'))
        with open(filename) as f:
            inf = f.readlines()
        self.infstring = inf
        self.R = int(inf[3])
        self.R2 = int(inf[4])
        self.cols = int(inf[6])
        self.rows = int(inf[7])
        self.S = float(inf[8])
        self.L = float(inf[9])
        if self.R != self.R2:
            warnings.warn('The Pixels of the IP picture are no squares.')

    def topsl(self, c):
        """
        returns the PSL value corresponding to the count number c at the
        readout settings defined by this Infreader object.
        """
        return cnttopsl(c, self.R, self.S, self.L)

    def __str__(self):
        return '<"' + self.name + '" R:' + str(self.R) + ' cols:' + \
               str(self.cols) + ' rows:' + str(self.rows) + ' S:' + \
               str(self.S) + ' L:' + str(self.L) + '>'

    def __eq__(self, other):
        '''
        returns True if equal IP read out settings were used.
        '''
        settings = ['R', 'R2', 'cols', 'rows', 'S', 'L']
        return all([getattr(self, s) == getattr(other, s) for s in settings])


class IPreader(Infreader):
    '''
    returns an IPreader Object, that allows access to the PSL converted
    Image 'self.psl'. This is derived from the class Infreader since all
    combined images MUST have identical read out settings.

    *args can be

    - a single file with '.img' or '.inf' or no extension.
      In this case this single file is read and converted.
    - a single filename that can be extended into multiple filenames
      by 'glob.glob(filename)'. Those files are then processed as follows:
    - multiple files of the former type. In this case it is assumed,
      that all files are multiple readouts
      of the same image plate in alpha-numerical order.
      All files are read and the program will try to combine them to a
      single image with higher dynamic range.

    The returned IPreader object will have the following attributes:

    - self.scalefactors - list of floats each readout needs to be
      multiplied by
    - self.scalefactorsstd - list of floats of standard deviation
      of scalefactors
    - self.psl - the high dynamic range image created by combining
      the images in self.psls using self.scalefactors
    '''

    def __init__(self, *args, **kwargs):
        raw_underexposed = kwargs.pop('raw_underexposed', 42000.0)
        raw_overexposed = kwargs.pop('raw_overexposed', 65525.0)
        if len(kwargs) > 0:  # unused kwargs left
            raise TypeError('unknown kwargs given: {:}'.format(kwargs))
        if len(args) == 1:
            self.files = glob.glob(args[0])
        elif len(args) > 1:  # List of filenames given
            self.files = args
        self.files = [f.strip('.img') for f in self.files]
        self.files = [f.strip('.inf') for f in self.files]
        # make list unique, so every file is only read once if
        # name* results in a list containing .img and .inf files.
        self.files = list(set(self.files))
        self.files.sort()

        Infreader.__init__(self, self.files[0] + '.inf')
        for f in self.files:
            if not self == Infreader(f + '.inf'):
                raise Exception('File "' + f + '" was read using different '
                                'read out settings. Refusing HDR assembly.')

        self.raw = [readimg(datei, self.rows, self.cols)
                    for datei in self.files]
        # Combine psl pictures to a single HDR picture
        self.rawsaturate = raw_overexposed
        self.rawminimum = raw_underexposed
        self.scalefactors = np.array([1.0])
        self.scalefactorsstd = np.array([0.0])
        sfvar = np.array([0.0])
        for n in range(1, len(self.raw)):
            A = self.getimgquotient(n - 1)
            meand = np.median(A[np.isfinite(A)])
            varianzd = np.var(A[np.isfinite(A)])
            mean = self.scalefactors[n - 1] * meand
            varianz = self.scalefactors[n - 1] ** 2 * varianzd + \
                sfvar[n - 1] * meand ** 2 + \
                varianzd ** 2 * sfvar[n - 1] ** 2
            self.scalefactors = np.append(self.scalefactors, mean)
            sfvar = np.append(sfvar, varianz)
        self.scalefactorsstd = np.sqrt(sfvar)

        # check consistency
        if not all(self.scalefactors == sorted(self.scalefactors)):
            warnings.warn('IP Files were not given is ascending read out '
                          'order! '
                          'This reduces quality of the assembled picture '
                          'dramatically or makes it even impossible!')
        if any(self.scalefactors < 1):
            warnings.warn('PSL SCALE HAS CHANGED because the first file is '
                          'always forced to have the scalefactor 1, but first '
                          'file is NOT the first readout of the IP '
                          '(in other words: there is at least one'
                          'scalefactor < 1).')

        # Assemble HDR Image in raw scale
        self.raw_hdr = np.zeros(self.raw[0].shape)
        count = np.zeros(self.raw[0].shape)
        for n in range(len(self.raw)):
            if np.isnan(self.scalefactors[n]):
                continue
            picn = copy.copy(self.raw[n])
            picn[picn > self.rawsaturate] = 0
            self.raw_hdr += self.scalefactors[n] * picn
            count += (picn > 0)
        count[count == 0] = 1  # prefents dividing by zero
        self.raw_hdr /= count

    # Creats raw data, which is reduced by over- and underexposure
    def _getrealimg(self, n):
        realimg = copy.copy(self.raw[n])
        realimg[(realimg > self.rawsaturate) | (realimg < self.rawminimum)] = np.nan
        return realimg

    # Creats the quotien between picture n and the following picture
    def getimgquotient(self, n):
        imgquotient = self._getrealimg(n) / self._getrealimg(n + 1)
        return imgquotient

    def plotscalefactors(self):
        '''
        Plots the distribution of scalefactors between consecutive images.
        This is to check manually that the hdr image assembly is done correctly.
        '''
        import matplotlib.pylab as plt

        print('Scalefactors for HDR-assembling are', self.scalefactors)
        print('Standard deviations for Scalefactors are', self.scalefactorsstd)

        # Plots the scalefactordistribution and scalefactors for each pixelvalue
        self.scaleforpix = range(len(self.raw))
        for n in range(len(self.raw) - 1):
            A = self.getimgquotient(n)
            B = self._getrealimg(n + 1)
            fig = plt.figure()
            plt.xlabel('x [pixel]')
            plt.ylabel('y [pixel]')
            fig.set_size_inches(10, 10)
            plt.imshow(A)
            plt.clim([0.95 * A[np.isfinite(A)].min(), 1.05 * A[np.isfinite(A)].max()])
            plt.colorbar()
            fig = plt.figure()
            linplotdata = np.array([B[np.isfinite(B)].flatten(), A[np.isfinite(B)].flatten()])
            plt.plot(linplotdata[0, :], linplotdata[1, :], 'ro')

    @property
    def psl(self):
        return self.topsl(self.raw_hdr)

    def __str__(self):
        return '<"' + str(self.files) + '" R:' + str(self.R) \
            + ' cols:' + str(self.cols) + ' rows:' + str(self.rows) \
            + ' S:' + str(self.S) + ' L:' + str(self.L) + '\n' \
            + 'Scalefactors:    ' + str(self.scalefactors) + '\n' \
            + 'Scalefactorsstd: ' + str(self.scalefactorsstd) + ' >'


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Previews the Image Plate'
                                     'readout(s) using matplotlib.')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('file', nargs='+',
                        help='input file(s) - can be *.inf or *.img or '
                        'without extension.')
    parser.add_argument('-l',
                        help='list properties of assembled image, dont '
                        'create any plots. No matplotlib is needed.',
                        action='store_true')
    parser.add_argument('--log',
                        help='creates a log10 plot instead of a linear one.',
                        action='store_true')
    parser.add_argument('-s', nargs='?', metavar='filename', dest='save',
                        help='save picture of data using matplotlib. '
                        'If this is given, no interactive window will appear.'
                        ' filename will be auto-generated if omitted.',
                        default='')
    parser.add_argument('-v', '--verbose', action='count',
                        help='Verbose output. This shows an additional plot'
                        'to verify the scalefactors calculated')
    args = parser.parse_args()
    if args.save is None:
        args.save = args.file[0] + '.png'
    elif args.save == '':
        args.save = None
    # now args.save cointains the savename or None

    ip = IPreader(*args.file)
    print(ip)

    if args.l:
        exit()

    # create plots
    import matplotlib
    if args.save:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # data plot
    if args.log:
        fig = plt.imshow(np.log10(ip.psl))
    else:
        fig = plt.imshow(ip.psl)
    plt.colorbar()
    if args.save:
        plt.savefig(args.save, dpi=400, transparent=True)
    else:
        plt.show(block=True)

    # scalefactor plot
    if args.verbose:
        ip.plotscalefactors()
        plt.show(block=True)


if __name__ == '__main__':
    main()

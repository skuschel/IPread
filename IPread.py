'''
Module providing the IPreader class for reading Image Plates data files. Multiple Files
can be combined to one Picture. Automatic PSL conversion is applied.

Author: Stephan Kuschel
'''

import numpy as np
import os
import warnings
import glob
import copy


class _Infreader():

    def __init__(self, filename):
        '''
        Filename must be the .inf file of the IP Scanner
        '''
        self.filename = filename
        self.name = os.path.basename(filename.strip('\n'))
        with open(filename) as f:
            inf = f.readlines()
        self.infstring = inf
        self.R = int(inf[3])
        self.R2 = int(inf[4])
        self.cols = int(inf[6])
        self.rows = int(inf[7])
        self.S = int(inf[8])
        self.L = int(inf[9])
        if self.R != self.R2:
            warnings.warn('The Pixels of the IP picture are no squares.')


    def topsl(self, c):
        return (self.R / 100.) ** 2 * (4000. / self.S) * 10.**(self.L * (c / 65536.0 - 0.5))

    def __str__(self):
        return '<"' + self.name + '" R:' + str(self.R) + ' cols:' + str(self.cols) + ' rows:' + str(self.rows) + ' S:' + str(self.S) + ' L:' + str(self.L) + '>'

    def __eq__(self, other):
        '''
        returns True if equal IP read out settings were used.
        '''
        settings = ['R', 'R2', 'cols', 'rows', 'S', 'L']
        return all([getattr(self, s) == getattr(other, s) for s in settings])


class IPreader(_Infreader):

    def __init__(self, filename):
        '''
        if extension is given read only single file.
        if no extension is given read and combine all files of pattern filname + '*'
        '''
        self.files = glob.glob(filename)
        self.files = [f.strip('.img') for f in self.files]
        self.files.sort()

        _Infreader.__init__(self, self.files[0] + '.inf')
        for f in self.files:
            if not self == _Infreader(f + '.inf'):
                raise Exception('File "' + f + '" was read using different read out settings. Refusing HDR assembly.')

        dt = np.dtype(np.uint16)
        dt = dt.newbyteorder('>')  # change to big endian
        self.psls = []
        for f in self.files:
            with open(f + '.img', 'rb') as f:
                raw = np.fromfile(f, dtype=dt)
                raw = np.array(np.reshape(raw, (self.rows, self.cols)), dtype=np.float64)
                self.psls.append(self.topsl(raw))

        # Combine psl pictures to a single HDR picture
        pslsaturate = self.topsl(65525.0)
        pslminimum = pslsaturate / 4.0
        self.scalefactors = np.array([1.0])
        self.scalefactorsstd = np.array([0.0])
        sfvar = np.array([0.0])
        piclast = copy.copy(self.psls[0])
        piclast[piclast > pslsaturate] = np.nan
        piclast[piclast < pslminimum] = np.nan
        for n in xrange(1, len(self.psls)):
            picnext = copy.copy(self.psls[n])
            picnext[picnext > pslsaturate] = np.nan
            picnext[picnext < pslminimum] = np.nan
            A = piclast / picnext
            meand = np.median(A[np.isfinite(A)])
            varianzd = np.var(A[np.isfinite(A)])
            mean = self.scalefactors[n - 1] * meand
            varianz = self.scalefactors[n - 1] ** 2 * varianzd + sfvar[n - 1] * meand ** 2 + varianzd ** 2 * sfvar[n - 1] ** 2
            self.scalefactors = np.append(self.scalefactors, mean)
            sfvar = np.append(sfvar, varianz)
            piclast = picnext
        self.scalefactorsstd = np.sqrt(sfvar)

        # Assemble HDR Image in PSL scale
        self.psl = np.zeros(piclast.shape)
        count = np.zeros(piclast.shape)
        for n in xrange(len(self.psls)):
            if np.isnan(self.scalefactors[n]):
                continue
            picn = copy.copy(self.psls[n])
            picn[picn > pslsaturate] = 0
            self.psl = self.psl + self.scalefactors[n] * picn
            count = count + (picn > 0)
        self.psl = self.psl / count


    def __str__(self):
        return '<"' + str(self.files) + '" R:' + str(self.R) + ' cols:' + str(self.cols) + ' rows:' + str(self.rows) \
            + ' S:' + str(self.S) + ' L:' + str(self.L) + '\n' \
            + 'Scalefactors:    ' + str(self.scalefactors) + '\n' \
            + 'Scalefactorsstd: ' + str(self.scalefactorsstd) + ' >'


# Command Line interface if started as a script and not imported
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('GTKAgg')
    import matplotlib.pyplot as plt
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='input file')
    args = parser.parse_args()

    ip = IPreader(args.file)
    print ip

    plt.imshow(ip.psl)
    plt.show(block=True)




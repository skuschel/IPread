'''
Module providing the IPreader class for reading Image Plates data files. Multiple Files
can be combined to one Picture. Automatic PSL conversion is applied.

Author: Stephan Kuschel
'''

import numpy as np
import os
import warnings


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
        return (self.R / 100.) ** 2 * (4000. / self.S) * 10.**(self.L * (c / 65536. - 0.5))

    def __str__(self):
        return '<"' + self.name + '" R:' + str(self.R) + ' cols:' + str(self.cols) + ' rows:' + str(self.rows) + ' S:' + str(self.S) + ' L:' + str(self.L) + '>'



class IPreader(_Infreader):

    def __init__(self, filename):
        '''
        filename must be given without extension.
        '''
        _Infreader.__init__(self, filename + '.inf')
        with open(filename + '.img') as f:
            data = np.fromfile(f, dtype=np.uint16)
        self.raw = np.reshape(data, (self.cols, self.rows))
        self.raw = np.float64(self.raw)
        self.psl = self.topsl(self.raw)



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
    print str(ip.psl)






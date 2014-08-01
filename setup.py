#!/usr/bin/python2

from setuptools import setup
from ipread import __version__
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='ipread',
      version=__version__,
      author='Stephan Kuschel',
      author_email='stephan.kuschel@gmail.com',
      description='Reads Imageplate files and combines multiple readouts to '
                  'a single HDR if necessary. Can be used as module or '
                  'with "python -m ipread" to have a CLI tool for '
                  'fast preview.',
      long_description=read('README.md'),
      url='https://github.com/skuschel/IPread',
      py_modules=['ipread'],
      scripts=['scripts/ipread'],
      install_requires=['matplotlib', 'numpy'],
      classifiers=[
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Astronomy',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Scientific/Engineering :: Visualization']
      )

#!/usr/bin/python

from setuptools import setup
from ipread import __version__
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='ipread',
    version=__version__,
	author='Stephan Kuschel',
	author_email='stephan.kuschel1@gmail.com',
	description='Reads Imageplate files and combines multiple readouts to a single HDR if necessary. Can be used as module or with "python -m IPread" to have a CLI tool for fast preview.',
	long_description=read('README.md'),
    url='https://github.com/skuschel/IPread',
    py_modules=['ipread'],
	install_requires=['matplotlib', 'numpy']
	)

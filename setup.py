#!/usr/bin/python

from setuptools import setup
from ipread import __version__

setup(name='IPread',
    version=__version__,
	author='Stephan Kuschel',
	author_email='stephan.kuschel1@gmail.com',
	description='Reads Imageplate files and combines multiple readouts to a singe HDR if necessary. Can be used as module or with "python -m IPread" to have a CLI tool for fast preview.',
	py_modules=['ipread'],
	install_requires=['matplotlib', 'numpy']
	)

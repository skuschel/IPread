IPread
======
[![Build Status](https://travis-ci.org/skuschel/IPread.svg?branch=master)](https://travis-ci.org/skuschel/IPread)
[![version](https://img.shields.io/pypi/v/ipread.svg)](https://pypi.python.org/pypi/ipread/)
[![Documentation Status](https://readthedocs.org/projects/ipread/badge/?version=latest)](http://ipread.readthedocs.org)

Python Module for reading Image Plates and combining several readouts to a single Image converted to PSL scale.


Installing
----------
### Install from github (recommended)

IPread can be installed directly from github via pip by running:

`pip install --user git+https://github.com/skuschel/IPread.git`


### IPread's latest release is available on [pypi](https://pypi.python.org/pypi/ipread/)

IPread is available in the python package index, thus it can be installed by using the python package manager pip:

`pip install ipread`

pip will download and install the latest version from [pypi](https://pypi.python.org/pypi/ipread/), thus no manual download is required. This is surely the easiest way to install ipread.


### Don't install, just use

Just copy `ipread.py` into your working directory and use `import ipread` in any python script in that directory.


### install in userspace

this will allow to access the package via `import ipread` from everywhere, but only for a single user.

`./setup.py install --user`


### install globally

With admin rights you can install IPread for all user of this computer by running:

`./setup.py install`



Using the Command-line-interface
--------------------------------

The CLI will provide an easy and fast way to run the python module as a script to preview any image plate files using matplotlib. After installing, just run

`ipread -h`

for further instructions. In case your system is configured to read executables from a python specific script path, the command `ipread` will serve as an alias to `python -m ipread` after installation.


Troubleshooting
---------------
Please use the [issue tracker](https://github.com/skuschel/IPread/issues/new) to ask user questions, report bugs or unexpected behavior. Thanks!

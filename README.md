IPread
======
[![Build Status](https://travis-ci.org/skuschel/IPread.svg?branch=master)](https://travis-ci.org/skuschel/IPread)

Python Module for reading Image Plates and combining several readouts to a single Image converted to PSL scale.


Installing
----------
### IPread is now available on [pypi](http://pypi.python.org/pypi/ipread/)

IPread is available in the python package index, thus it can be installed by using the python package manager pip:

`pip install ipread`

pip will download and install the latest version from [pypi](http://pypi.python.org/pypi/ipread/), thus no manual download is required. This is surely the easiest way to install ipread. 

### Don't install, just use

Just copy ipread.py into your working directory and use `import ipread` in any python script in that directory.

### install in userspace

this will allow to access the package via `import ipread` from everywhere, but only for a single user.

`python2 setup.py install --user`

### install global

you will need admin rights, then run

`python2 setup.py install`



Using the Command-line-interface
--------------------------------

The CLI will provide an easy and fast way to run the python module as a script to preview any image plate files using matplotlib. After installing, just run

`python2 -m ipread -h`

for further instructions. In case your system is configured to read executables from a python specific script path, the command `ipread` will serve as an alias to `python2 -m ipread` after installation.

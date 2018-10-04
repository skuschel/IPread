#!/bin/bash

# runs the tests.
# It is recommended to link this script as a git pre-commit hook via:
#
# ln -s ../../run-tests.sh .git/hooks/pre-commit
#
set -e


pycodestyle ipread.py --statistics --count --show-source --ignore=W391 --max-line-length=99

python -m ipread -h

mkdir -p _testdata
cd _testdata

# some example data found on the internet...
wget --no-clobber http://public.gettysburg.edu/~bcrawfor/physics/nHe4/BeamImages/output.inf
wget --no-clobber http://public.gettysburg.edu/~bcrawfor/physics/nHe4/BeamImages/output.img

ipread output* -v -s final.png
ipread output* -v --log -s final_log.png

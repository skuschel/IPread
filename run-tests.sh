#!/bin/bash

# runs the tests.
# It is recommended to link this script as a git pre-commit hook via:
#
# ln -s ../../run-tests.sh .git/hooks/pre-commit
#

pycodestyle ipread.py --statistics --count --show-source --ignore=W391 --max-line-length=99

python -m ipread -h

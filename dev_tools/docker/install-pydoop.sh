#!/bin/bash

HDFS_BACKEND=native

# current path
script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install pydoop
cd $script_path

# removing existing versions
# TODO: update with a more general cleaner
rm -Rf /root/.local/lib/python2.7/site-packages/pydoop*

# clean install dir
make clean

# install pydoop
python setup.py build --hdfs-core-impl $HDFS_BACKEND
python setup.py install --user --skip-build

# run tests
cd test && python all_tests.py
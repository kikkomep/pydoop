#!/bin/bash

HDFS_BACKEND=native

# current path
script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install pydoop
cd $script_path
python setup.py build --hdfs-core-impl $HDFS_BACKEND
python setup.py install --user --skip-build

# run tests
cd test && python all_tests.py
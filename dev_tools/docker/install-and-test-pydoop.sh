#!/bin/bash

# current path
script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#
source ${script_path}/install-pydoop.sh "$@"

# run tests
cd test && python all_tests.py
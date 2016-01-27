#!/bin/bash

HDFS_BACKEND="native"

# current path
script_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# find the pydoop package folder
dir=$(python - <<EOF
import os
import pkgutil

if pkgutil.find_loader('pydoop'):
    import pydoop
    print os.path.dirname(pydoop.__file__) + "/../.."
EOF
)

# removing existing versions
if [[ -n ${dir} ]]; then
    echo "found directory"
    rm -Rf ${dir}/pydoop*
else
    echo "No Pydoop version installed!!!"
fi

# set the working dir
working_dir="${script_path}/../../"
cd ${working_dir}

# clean install dir
make clean

# install pydoop
python setup.py build --hdfs-core-impl ${HDFS_BACKEND}
python setup.py install --user --skip-build
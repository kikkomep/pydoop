#!/bin/bash

HDFS_BACKEND="native"

if [[ -n $1 ]]; then
    HDFS_BACKEND=$1
fi

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

# install JPype
if [[ $HDFS_BACKEND == "jpype-bridged"  ]]; then cd /tmp; git clone https://github.com/originell/jpype.git; cd jpype; python setup.py install; fi
#- if [[ $HDFS_BACKEND == "jpype-bridged" ]]; then wget http://sourceforge.net/projects/jpype/files/JPype/0.5.4/JPype-0.5.4.2.zip; unzip JPype-0.5.4.2.zip; cd JPype-0.5.4.2; $VIRTUAL_ENV/bin/python setup.py install; cd ../; fi

# set the working dir
working_dir="${script_path}/../../"
echo "Working DIR: ${working_dir}"
cd ${working_dir}

# clean install dir
make clean

# install pydoop
python setup.py build --hdfs-core-impl ${HDFS_BACKEND}
python setup.py install --user --skip-build
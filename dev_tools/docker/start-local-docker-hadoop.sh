#!/usr/bin/env bash

# current path
CURRENT_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# images path
IMAGES_PATH="${CURRENT_PATH}/images"

# the docker repository
DOCKERHUB_REPOSITORY="crs4"

# the dockerhub image prefix
DOCKERHUB_IMAGE_PREFIX="hadoop"

# print usage
usage() {
    echo -e "\nUsage: $0 [-r|--repository <REPO_NAME>] [-p|--prefix <IMAGE_PREFIX>] <HADOOP_DISTRO>";
    echo -e "       e.g.: $0 -r crs4 -p docker hadoop-2.7.1";
    exit 1;
}

# parse arguments
OPTS=`getopt -o r:p: --long "repository:,prefix:" -n 'parse-options' -- "$@"`

# check parsing result
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; usage; exit 1 ; fi

# process arguments
eval set -- "$OPTS"
while true; do
  case "$1" in
    -r | --repository ) DOCKERHUB_REPOSITORY="$2"; shift; shift ;;
    -p | --prefix ) DOCKERHUB_IMAGE_PREFIX="$2"; shift; shift ;;
    --help ) usage; exit 0; shift ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done


# image to build
HADOOP_DISTRO=${1}

# check whether the name has been provided
if [[ -z "$HADOOP_DISTRO" ]]; then
	usage
	exit -1
fi

# image prefix
DOCKERHUB_REPOSITORY_IMAGE_PREFIX="${DOCKERHUB_REPOSITORY}/${DOCKERHUB_IMAGE_PREFIX}-"

# docker image
DOCKERHUB_IMAGE="${DOCKERHUB_REPOSITORY_IMAGE_PREFIX}${HADOOP_DISTRO}"

# start docker-hadoop
docker run -it -d -v "${CURRENT_PATH}/../../":/sharing -h docker-hadoop --name hadoop-docker ${DOCKERHUB_IMAGE} start-hadoop-services
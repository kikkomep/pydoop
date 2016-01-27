#!/usr/bin/env bash
docker run -it --rm -h docker-hadoop -v $(pwd):/sharing crs4/hadoop-apache-2.7.1 start-hadoop-services /bin/bash /sharing/.docker-travis-tests.sh

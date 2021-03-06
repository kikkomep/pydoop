#!/bin/bash

#--- manage_deamon stardard
export HADOOP_LOG_DIR=${HDFS_LOG_DIR}
export HADOOP_PID_DIR=${HDFS_PID_DIR}

python /tmp/zk_wait.py namenode

su -l ${HDFS_USER} -c "${HADOOP_HOME}/bin/hdfs --config ${HADOOP_CONF_DIR} namenode -format"

su -l -p ${HDFS_USER} -c "${HADOOP_HOME}/sbin/hadoop-daemon.sh --config ${HADOOP_CONF_DIR} start namenode"

# we should actually check that the namenode is up ...
python /tmp/zk_set.py namenode up

echo "log is ${HDFS_LOG_DIR}/*namenode-${HOSTNAME}.out"

tail -f ${HDFS_LOG_DIR}/*namenode-${HOSTNAME}.out

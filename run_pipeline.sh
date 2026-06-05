#!/bin/bash

set -e   

#Python 버전 &  인코딩 설정 

export PYSPARK_PYTHON=/usr/bin/python3.6
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.6
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8


echo "Spark 전처리 (process.py)"
spark-submit src/pipeline/process.py 2>&1 | grep -v WARN

echo "HDFS 권한 설정"
hdfs dfs -chmod -R 777 /user/maria_dev/news-stock/processed


echo "Hive 분석(query.hql)"
hive -f src/pipeline/query.hql 2>/dev/null

echo " 파이프라인 완료"




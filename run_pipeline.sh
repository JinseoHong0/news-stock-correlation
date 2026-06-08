#!/bin/bash

set -e   

#Python 버전 &  인코딩 설정 

export PYSPARK_PYTHON=/usr/bin/python3.6
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.6
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8


if [ ! -d "data/knu_senti" ]; then
    git clone https://github.com/park1200656/KnuSentiLex data/knu_senti
    echo "  KNU 사전 clone 완료"
else
    echo "  KNU 사전 이미 존재, 건너뜀"
fi



echo "Spark 전처리 (process.py)"
spark-submit src/pipeline/process.py 2>&1 | grep -v WARN

echo "HDFS 권한 설정"
hdfs dfs -chmod -R 777 /user/maria_dev/news-stock/processed


echo "Hive 분석(query.hql)"
hive -f src/pipeline/query.hql 2>/dev/null


hdfs dfs -cat /user/maria_dev/news-stock/result/q1_market/* > result/q1_market.csv

hdfs dfs -cat /user/maria_dev/news-stock/result/q2_category/* > result/q2_category.csv

hdfs dfs -cat /user/maria_dev/news-stock/result/q3_positive/* > result/q3_positive.csv

hdfs dfs -cat /user/maria_dev/news-stock/result/q3_negative/* > result/q3_negative.csv


echo " 파이프라인 완료"

echo "===== 분석 결과 확인 ====="
echo "[Q1] 시장별 지수 상관계수"
cat result/q1_market.csv
echo ""
echo "[Q2] 카테고리별 상관계수"
cat result/q2_category.csv
echo ""
echo "[Q3-A] 동조 종목 Top 20"
cat result/q3_positive.csv
echo ""
echo "[Q3-B] 역행 종목 Top 20"
cat result/q3_negative.csv

mkdir -p charts
python3.6 src/analyze/dashboard.py
echo "result chart generated"


# -*- coding: utf-8 -*-

import json
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

spark = SparkSession.builder.appName("news-stock-preprocess").getOrCreate()
HDFS = "/user/maria_dev/news-stock"
SENTI_PATH = "data/knu_senti/data/SentiWord_info.json"


# load KNU dic
with open(SENTI_PATH, encoding="utf-8") as f:
    raw = json.load(f)
senti_dict = {item["word"]: int(item["polarity"]) for item in raw}
print(" 감성사전 단어 수:", len(senti_dict))

senti_bc = spark.sparkContext.broadcast(senti_dict)

def score_title(title):
    if title is None:
        return 0
    d = senti_bc.value
    return sum(d.get(tok, 0) for tok in title.split())
 
score_udf = F.udf(score_title, IntegerType())


# 1. 주가불러오기


def load_market(folder, market_name):
    df = spark.read.csv("{}/{}/*.csv".format(HDFS, folder),
                        header="true", inferSchema="true")
    df = df.withColumn("Code", F.lpad(F.col("Code").cast("string"), 6, "0"))
    return df.withColumn("market", F.lit(market_name))
 
kospi = load_market("kospi_ticker", "KOSPI")
kosdaq = load_market("kosdaq_ticker", "KOSDAQ")
stock = kospi.union(kosdaq)
print(" 주가 전체 행 수:", stock.count())

stock = stock.withColumn("dow", F.dayofweek("Date"))
stock = stock.withColumn("week_key",
                         F.expr("date_sub(Date, (dow - 2 + 7) % 7)"))

#주별 종목별 평균 수익율
weekly_ret = stock.groupBy("week_key", "market").agg(
    F.avg("Change").alias("avg_return")
)

print("주별 수익률 샘플:")
weekly_ret.orderBy("week_key").show(5)


#주별 종목별 수익률
stock_weekly = stock.groupBy("week_key", "market", "Code").agg(
    F.avg("Change").alias("stock_return")
)


#지수 불러오기
def load_index(filename, market_name):
    df = spark.read.csv("{}/index/{}".format(HDFS, filename),
                        header="true", inferSchema="true")
    return df.withColumn("market", F.lit(market_name))

idx_kospi = load_index("KOSPI_16to20.csv", "KOSPI")
idx_kosdaq = load_index("KOSDAQ_16to20.csv", "KOSDAQ")
index = idx_kospi.union(idx_kosdaq)

index = index.withColumn("dow", F.dayofweek("Date"))
index = index.withColumn("week_key",
                         F.expr("date_sub(Date, (dow - 2 + 7) % 7)"))

weekly_index = index.groupBy("week_key", "market").agg(
    F.avg("Change").alias("index_return")
)
print("지수 주별 수익률 샘플:")
weekly_index.orderBy("week_key").show(5)

# 종목명+업종 매핑 테이블
def load_list(filename):
    df = spark.read.csv("{}/stock_list/{}".format(HDFS, filename),
                        header="true", inferSchema="true").select("Code", "Name", "Industry")
    # Code를 6자리 문자열로 통일 (조인 키 일치용)
    return df.withColumn("Code", F.lpad(F.col("Code").cast("string"), 6, "0"))

names = load_list("KOSPI_DESC.csv").union(load_list("KOSDAQ_DESC.csv"))



# 2.  뉴스 처리 (날짜 파싱, 카테고리 필터, 감성점수)
news = spark.read.csv("{}/news/klue_ynat_raw.csv".format(HDFS),
                      header="true", inferSchema="true")
 
# 날짜 파싱 앞 10자 '2016.06.30'
news = news.withColumn("date_str", F.substring("date", 1, 10))
news = news.withColumn("date_parsed", F.to_date("date_str", "yyyy.MM.dd"))
 
# 감성점수 (udf)
news = news.withColumn("sentiment", score_udf("title"))
news = news.withColumn("dow", F.dayofweek("date_parsed"))
news = news.withColumn("week_key",
                       F.expr("date_sub(date_parsed, (dow - 2 + 7) % 7)"))

 
# 주별 x 카테고리별 평균 감성
weekly_senti = news.groupBy("week_key", "category").agg(
    F.avg("sentiment").alias("avg_sentiment"),
    F.count("*").alias("n_articles")
)

#주별 전체 평균 감성
weekly_senti_all = news.groupBy("week_key").agg(
    F.avg("sentiment").alias("avg_sentiment"),
    F.count("*").alias("n_articles")
)

print("주별 감성 샘플:")
weekly_senti.orderBy("week_key").show(10)


# 3. 조인 + 저장

#카테고리별 감성-시장별 종목 수익
result = weekly_senti.join(weekly_ret, on="week_key", how="inner")
print(" 조인 결과 샘플:")
result.orderBy("week_key").show(10)
print("조인 결과 행 수:", result.count())
 

result.write.mode("overwrite").option("header", "true").csv("{}/processed/weekly_joined".format(HDFS))
print("개별 종목 저장경로:", "{}/processed/weekly_joined".format(HDFS))


# 감성x 시장별 지수

result_index = weekly_senti_all.join(weekly_index, on="week_key", how="inner")
print("지수 조인 결과 행 수:", result_index.count())
result_index.orderBy("week_key").show(5)

result_index.write.mode("overwrite").option("header", "true").csv(
    "{}/processed/weekly_index".format(HDFS))

print("지수 저장경로", "{}/processed/weekly_index".format(HDFS))

#전체 감성-개별종목 수익률
result_stock = stock_weekly.join(weekly_senti_all, on="week_key", how="inner") \
                           .join(names, on="Code", how="left")

print("종목별 조인 행 수:", result_stock.count())
print("종목별 결과 컬럼 순서:", result_stock.columns)
result_stock.orderBy("week_key").show(5)
result_stock.write.mode("overwrite").option("header", "true").csv(
    "{}/processed/weekly_stock".format(HDFS))

spark.stop()

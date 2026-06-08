

--종목 수익률 평균x카테고리 감성 테이블
DROP TABLE IF EXISTS weekly_joined_external;
CREATE EXTERNAL TABLE IF NOT EXISTS weekly_joined_external (
    week_key        STRING,
    category        STRING,
    avg_sentiment   DOUBLE,
    n_articles      INT,
    market          STRING,
    avg_return      DOUBLE
)

ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/news-stock/processed/weekly_joined'
TBLPROPERTIES ("skip.header.line.count"="1");


-- 주별 지수 테이블 가져오기
DROP TABLE IF EXISTS weekly_index_external;
CREATE EXTERNAL TABLE IF NOT EXISTS weekly_index_external (
    week_key        STRING,
    avg_sentiment   DOUBLE,
    n_articles      INT,
    market          STRING,
    index_return    DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/news-stock/processed/weekly_index'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 개별 종목 x 전체 감성
DROP TABLE IF EXISTS weekly_stock_external;
CREATE EXTERNAL TABLE IF NOT EXISTS weekly_stock_external (
    code            STRING,
    week_key        STRING,
    market          STRING,
    stock_return    DOUBLE,
    avg_sentiment   DOUBLE,
    n_articles      INT,
    name            STRING,
    industry        STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/maria_dev/news-stock/processed/weekly_stock'
TBLPROPERTIES ("skip.header.line.count"="1");



-- 뉴스 카테고리별 주간 뉴스 감성과 주간 수익률 상관분석


-- [분석 질문 1] 주간 뉴스 감성과  지수 변동의 상관
INSERT OVERWRITE DIRECTORY '/user/maria_dev/news-stock/result/q1_market'
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
SELECT
    market,
    COUNT(week_key),
    CORR(avg_sentiment, index_return)
FROM weekly_index_external
GROUP BY market;

-- [분석 질문 2] 카테고리별 뉴스 감성과 수익률 상관 
INSERT OVERWRITE DIRECTORY '/user/maria_dev/news-stock/result/q2_category'
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
SELECT
    category,
    COUNT(week_key),
    SUM(n_articles),
    -- Hive 내장 피어슨 상관계수 함수 활용
    CORR(avg_sentiment, avg_return) AS correlation_coefficient
FROM weekly_joined_external
WHERE n_articles >= 5  -- 노이즈 방지를 위해 기사 수가 너무 적은 주(week)는 제외
GROUP BY category
ORDER BY ABS(correlation_coefficient) DESC;



-- [분석 질문 3] 전체 주간 감성에 가장 영향을 많이 받은 종목 Top 20
-- (최소 100주 이상 거래된 종목만)

--양의 상관
INSERT OVERWRITE DIRECTORY '/user/maria_dev/news-stock/result/q3_positive'
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
SELECT
    code,
    name,
    regexp_replace(industry,'"',''),
    market,
    COUNT(week_key),
    CORR(avg_sentiment, stock_return) AS correlation_coefficient
FROM weekly_stock_external
GROUP BY code, name, industry, market
HAVING COUNT(week_key) >= 100
ORDER BY correlation_coefficient DESC
LIMIT 20;

--음의 상관
INSERT OVERWRITE DIRECTORY '/user/maria_dev/news-stock/result/q3_negative'
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
SELECT
    code,
    name,
    industry,
    market,
    COUNT(week_key),
    CORR(avg_sentiment, stock_return) AS correlation_coefficient  
FROM weekly_stock_external
GROUP BY code, name,industry,  market
HAVING COUNT(week_key) >= 100
ORDER BY correlation_coefficient ASC
LIMIT 20;


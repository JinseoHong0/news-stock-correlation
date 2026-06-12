# 뉴스 감성 × 주가 수익률 상관관계 분석

> 연합뉴스 헤드라인(KLUE-YNAT)의 주간 감성 점수와 KOSPI/KOSDAQ 주가 수익률의 상관관계를 분석하는 빅데이터 파이프라인

---

## 분석 질문

| # | 질문 | 데이터 |
|---|------|--------|
| Q1 | 주간 뉴스 감성이 주간 지수 수익률과 유의미한 상관을 보이는가? | 지수(KOSPI_16to20 / KOSDAQ_16to20) |
| Q2 | 카테고리별(경제/정치/세계 등)로 상관계수가 다르게 나타나는가? | 종목 시장평균 수익률 |
| Q3 | 전체 뉴스 감성에 가장 민감하게 반응한 개별 종목은? | 종목별 수익률 + 업종(Industry) |

---

## 기술 스택

```
데이터 수집    Python (FinanceDataReader, KLUE-YNAT)
분산 저장      HDFS
전처리         Apache Spark (PySpark DataFrame API)
분석           Apache Hive (HiveQL, CORR 함수)
시각화         Plotly (HTML 차트)
자동화         Shell Script (run_pipeline.sh)
실행 환경      HDP Sandbox (Python 3.6 / Spark 2.x / Hive 3.1 / CentOS 7)
```

---

## 데이터

| 데이터 | 출처 | 수집 방법 | 기간 | 규모 |
|--------|------|-----------|------|------|
| 뉴스 헤드라인 | KLUE-YNAT (연합뉴스) | HuggingFace datasets | 2016~2020 | 54,785건 |
| KOSPI/KOSDAQ 종목 주가 | FinanceDataReader | 종목별 분할 수집 | 2016~2020 | 약 239만 행 |
| KOSPI/KOSDAQ 지수 | FinanceDataReader | 스크립트 | 2016~2020 | KOSPI_16to20.csv / KOSDAQ_16to20.csv |

> **수집 환경**: KRX가 클라우드/데이터센터 IP를 차단하므로 데이터 수집은 로컬에서 수행 후 Sandbox에 업로드.

---

## 프로젝트 구조

```
news-stock-correlation/
├── README.md
├── charts                        # 최종 시각화 html 저장
├── requirements.txt              # 수집 환경 의존성 (Python 3.x)
├── run_ingest.sh                 # 데이터 수집 자동화 (로컬 실행)
├── run_pipeline.sh               # 전처리→분석→시각화 자동화 (Sandbox 실행)
├── data/
│   ├── raw/
│   │   ├── kospi_ticker/         # KOSPI 종목별 주가 CSV
│   │   ├── kosdaq_ticker/        # KOSDAQ 종목별 주가 CSV
│   │   ├── index/                # 지수 CSV (KOSPI_16to20, KOSDAQ_16to20)
│   │   ├── news/                 # 뉴스 CSV (klue_ynat_raw.csv)
│   │   └── stock_list/           # 종목 리스트 + DESC (Code, Name, Industry)
│   └── knu_senti/                # KNU 한국어 감성사전 (자동 clone)
└── src/
    ├── ingest/                   # 데이터 수집 스크립트
    │   ├── collect_stock_list.py # 종목 리스트 + 지수 수집
    │   ├── collect_kospi_ticker.py
    │   ├── collect_kosdaq_ticker.py
    │   └── collect_news.py       # KLUE-YNAT 뉴스 수집
    ├── pipeline/                 # 핵심 파이프라인
    │   ├── process.py            # Spark 전처리
    │   └── query.hql             # Hive 분석
    └── analyze/
        └── dashboard.py          # Plotly 시각화
```

---

## 파이프라인 흐름

```
[로컬] 데이터 수집 (run_ingest.sh)
    ↓ zip 압축 → scp → docker cp
[Sandbox] HDFS 적재
    ↓
[Sandbox] bash run_pipeline.sh
    ├── [0] KNU 감성사전 clone (없을 때만)
    ├── [1] Spark 전처리 (process.py)
    │       감성점수 계산 (KNU 사전 + 공백 split 매칭)
    │       주별 집계 (week_key = 그 주 월요일)
    │       weekly_joined / weekly_index / weekly_stock 3종 저장
    ├── [2] Hive 분석 (query.hql)
    │       Q1: 지수 기반 시장별 상관
    │       Q2: 카테고리별 상관
    │       Q3: 종목별 상관 (동조 Top20 / 역행 Top20)
    │       결과 → HDFS result/ 4개 디렉토리 저장
    ├── [3] 결과 로컬 추출 (hdfs dfs -getmerge)
    └── [4] 시각화 (dashboard.py → charts/*.html)
```

---

## 실행 방법

### 환경

- **Sandbox**: HDP Sandbox (Docker), Python 3.6, Spark 2.x, Hive 3.1
- **로컬**: Python 3.x (수집 재현 시)
- HDFS 경로: `/user/maria_dev/news-stock/`

### 1단계 — 데이터 준비 (로컬에서)

**직접 수집**
# 수집 실행 (KRX 클라우드 차단으로 반드시 로컬에서)
'''
bash pip install -r requirements.txt
bash run_ingest.sh
'''

### 2단계 — Sandbox로 데이터 전송

```bash
# 로컬에서 압축 후 VM으로
zip -r data.zip data/raw/
scp -i <키경로> data.zip <사용자>@<VM-IP>:~/

# VM에서 컨테이너로
sudo docker cp ~/data.zip sandbox-hdp:/home/maria_dev/

# 컨테이너(Sandbox)에서 압축 해제
cd ~
unzip data.zip
```

### 3단계 — HDFS 적재 (Sandbox에서)

```bash
# 코드 받기
git clone https://github.com/JinseoHong0/news-stock-correlation.git
cd news-stock-correlation

# 데이터를 프로젝트 폴더로 이동
cp -rf ~/data/raw/* data/raw/

# HDFS 적재
hdfs dfs -mkdir -p /user/maria_dev/news-stock
hdfs dfs -put data/raw/* /user/maria_dev/news-stock/

# 적재 확인
hdfs dfs -du -h /user/maria_dev/news-stock/
```

### 4단계 — 파이프라인 실행 (Sandbox에서)

```
bash cd ~/news-stock-correlation
bash pip3.6 install --user -r requirements.txt
bash run_pipeline.sh
```

한 번 실행으로 전처리 → 분석 → 시각화까지 자동 완료.

### 5단계 — 결과 확인

```bash
# 분석 결과 (상관계수)
cat result/q1_market.csv
cat result/q2_category.csv

# 차트 파일 목록
ls charts/
```

**차트 파일 (HTML)**
```
charts/q1_market.html       시장별 감성-지수 상관계수
charts/q2_category.html     카테고리별 상관계수 (양=파랑/음=빨강)
charts/q3_positive.html     동조 종목 Top 20
charts/q3_negative.html     역행 종목 Top 20
charts/q3_market_dist.html  Top 20의 KOSPI/KOSDAQ 분포
```


새 터미널 열어서 차트 html 로컬로 가져오기
# 1. 컨테이너에서 VM으로
ssh -i ~/gcp/gcptutorial <사용자>@<IP> "sudo docker cp sandbox-hdp:/home/maria_dev/news-stock-correlation/charts ~/charts_new"

# 2. VM에서 로컬로
scp -i ~/gcp/gcptutorial -r <사용자>@<VM-IP>:~/charts_new ~/Desktop/charts


> 위 방법이 경로 설정 문제상 실행되지 않을 경우에 대비하여 charts/ 폴더에 사전 생성된 차트가 포함되어 있으나, run_pipeline.sh 실행 시 새로 생성됩니다.

---

## 주요 분석 결과

### Q1 — 시장별 지수 상관계수
| 시장 | 상관계수 |
|------|---------|
| KOSDAQ | -0.075 |
| KOSPI  | -0.074 |

### Q2 — 카테고리별 상관계수
| 카테고리 | 상관계수 |
|---------|---------|
| 정치 | -0.100 |
| 스포츠 | -0.069 |
| 경제 | +0.062 |
| 사회 | -0.054 |
| 생활문화 | -0.049 |
| 세계 | +0.047 |
| IT과학 | +0.035 |

### Q3 — 개별 종목 (최대 ±0.24, 대부분 KOSDAQ)

---

## 한계 및 고려사항

- 감성점수는 공백 분리 정확 매칭 방식 (형태소 분석 미적용) → 조사·어미로 인한 미매칭 존재
- 전체 뉴스 기반 감성 (종목 단위 뉴스 아님) → 개별 종목과의 직접 인과 해석 유보
- 데이터 규모 156MB — 빅데이터 규모는 아니나, 확장 가능한 분산처리 파이프라인 구조로 설계
- 상관관계 분석이며 인과관계를 주장하지 않음

---

## AI 도구 사용

- Claude: Spark UDF 디버깅, Hive 쿼리 디버깅, 파이프라인 구조 설계 보조, 시각화 코드 디버깅

---

## 참고 자료

- KNU 한국어 감성사전: https://github.com/park1200656/KnuSentiLex
- KLUE-YNAT: https://huggingface.co/datasets/klue/klue (config: ynat)
- FinanceDataReader: https://github.com/FinanceData/FinanceDataReader
- Apache Spark DataFrame API: https://spark.apache.org/docs/latest/sql-programming-guide.html
- Apache Hive UDF (CORR): https://cwiki.apache.org/confluence/display/Hive/LanguageManual+UDF

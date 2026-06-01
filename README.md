# 뉴스 감성 점수와 KOSPI/KOSDAQ 주가 변동의 상관관계 분석

주간 뉴스 감성 점수가 긍정/부정일 때, 동일 주 주가 수익률과 어떤 상관관계를 보이는지 분석한다. KOSPI와 KOSDAQ을 비교군으로 설정하여 시장 유형에 따른 뉴스 민감도 차이도 함께 검증한다.

---

## 사용하는 데이터

| 데이터 | 출처 | 수집 방법 | 기간 |
|--------|------|-----------|------|
| 뉴스 헤드라인 | KLUE-YNAT (연합뉴스) | HuggingFace `load_dataset` | 2016 ~ 2020 |
| KOSPI 종목 주가 | FinanceDataReader | Python 스크립트 | 2016 ~ 2020 |
| KOSDAQ 종목 주가 | FinanceDataReader | Python 스크립트 | 2016 ~ 2020 |
| KOSPI 지수 (KS11) | FinanceDataReader | Python 스크립트 | 2016 ~ 2020 |
| KOSDAQ 지수 (KQ11) | FinanceDataReader | Python 스크립트 | 2016 ~ 2020 |

- **뉴스 대상**: 7개 카테고리(경제/정치/사회/세계/IT과학/생활문화/스포츠) 전체 수집, 카테고리별 감성-수익률 상관 비교
- **주가 대상**: 2016년 기준 상장 종목 전체 (KOSPI 약 900종목, KOSDAQ 약 1,700종목)
- **감성 분석**: KNU 한국어 감성사전 (단어 매칭 방식, 별도 모델 불필요)



### 분석 질문
1. 주간 뉴스 감성이 주간 수익률과 유의미한 상관을 보이는가?
2. 카테고리별(경제/정치/세계 등)로 상관계수가 다르게 나타나는가?
3. KOSPI와 KOSDAQ 중 어느 시장이 뉴스 감성에 더 민감하게 반응하는가?

---

## 기술 스택

```
데이터 수집       Python (FinanceDataReader, HuggingFace datasets)
분산 저장         HDFS (CSV)
전처리 · 분석     Apache Spark (DataFrame API, Spark SQL)
집계 · 웨어하우스  Apache Hive (HiveQL)
시각화            Plotly, Streamlit
자동화            Shell Script (run_pipeline.sh)
실행 환경         HDP Sandbox (Hortonworks, CentOS 7)
```

- Spark: 형태소 분석 기반 감성점수 계산, 주 단위 집계, 날짜 기준 조인, 상관계수 산출
- Hive: 카테고리별·시장별 집계 쿼리, 통계 테이블 생성

---

## 파이프라인

```
① 뉴스 수집     src/ingest/collect_news.py          → data/raw/news/
② 주가 수집     src/ingest/collect_stock_list.py     → data/raw/stock_list/
                src/ingest/collect_kospi_ticker.py   → data/raw/kospi_ticker/
                src/ingest/collect_kosdaq_ticker.py  → data/raw/kosdaq_ticker/
                (KS11, KQ11 지수 포함)               → data/raw/index/
③ HDFS 적재    hdfs dfs -put
④ Spark 전처리  src/pipeline/process.py              → 감성점수, 수익률, 주별 집계, 조인
⑤ Hive 집계    src/pipeline/query.hql               → 카테고리별·시장별 상관계수
⑥ 시각화       src/analyze/dashboard.py             → Streamlit 대시보드
```

전체 파이프라인은 `run_pipeline.sh` 한 번으로 실행:

```bash
bash run_pipeline.sh
```

---

## 프로젝트 구조

```
news-stock-correlation/
├── README.md
├── run_pipeline.sh
├── data/
│   ├── raw/
│   │   ├── news/               # KLUE-YNAT 뉴스 헤드라인
│   │   ├── kospi_ticker/       # KOSPI 종목별 일봉
│   │   ├── kosdaq_ticker/      # KOSDAQ 종목별 일봉
│   │   ├── stock_list/         # 종목 리스트 (KOSPI/KOSDAQ)
│   │   └── index/              # KS11, KQ11 지수
│   └── README.md               # 데이터 출처 및 스키마
├── src/
│   ├── ingest/
│   │   ├── collect_news.py         # KLUE-YNAT 뉴스 수집
│   │   ├── collect_stock_list.py   # 종목 리스트 + 지수 수집
│   │   ├── collect_kospi_ticker.py # KOSPI 종목 주가 수집
│   │   └── collect_kosdaq_ticker.py# KOSDAQ 종목 주가 수집
│   ├── pipeline/
│   │   ├── process.py          # Spark 전처리 (감성점수, 수익률, 조인)
│   │   ├── load.hql            # Hive 테이블 생성
│   │   └── query.hql           # Hive 분석 쿼리
│   └── analyze/
│       └── dashboard.py        # Streamlit 시각화
└── .gitignore
```

---

## 데이터 수집 재현

```bash
# 로컬(Python 3)에서 실행
pip install finance-datareader datasets

python src/ingest/collect_stock_list.py   # 종목 리스트 + 지수
python src/ingest/collect_kospi_ticker.py # KOSPI 주가
python src/ingest/collect_kosdaq_ticker.py# KOSDAQ 주가
python src/ingest/collect_news.py         # 뉴스 헤드라인
```

> 수집된 데이터(CSV)는 .gitignore에 의해 저장소에 포함되지 않는다.
> 위 스크립트를 실행하면 동일한 데이터를 재현할 수 있다.

---

## AI 도구 사용

- Claude: README 작성 보조, 분석 설계 방향 논의, 코드 디버깅 보조
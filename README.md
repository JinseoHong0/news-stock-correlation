# 뉴스 감성 점수와 KOSPI 주가 변동의 상관관계 분석

뉴스에서 "금리 인하"냐 "금리 인상"등의 특정 키워드에 따라
주가 반응이 다를 것 같아서 뉴스 키워드와 주가의 관계를 분석해본다.
BigKinds 경제 뉴스의 감성 점수를 일별로 집계하고,
같은 날 KOSPI 종목 수익률과 얼마나 연관이 있는지 분석한다.

---

## 사용하는 데이터

| 데이터 | 출처 | 수집 방법 | 기간 |
|--------|------|-----------|------|
| 경제 뉴스 | BigKinds API | REST API | 2020 ~ 2025 |
| KOSPI 주가 | FinanceDataReader | Python 스크립트 | 2020 ~ 2025 |

- 대상 종목: KOSPI 대형주 100종목 (섹터별 균등 선정)
- 감성 분석: KNU 한국어 감성사전 (단어 매칭 방식, 별도 모델 불필요)

---

## 기술 스택 예상

```
데이터 수집       Python (BigKinds API, FinanceDataReader)
분산 저장         HDFS (CSV, Parquet)
전처리 · 분석     Apache Spark (DataFrame API, Spark SQL)
집계 · 웨어하우스  Apache Hive (HiveQL)
시각화            Plotly, Streamlit, Seaborn
자동화            Shell Script (run_pipeline.sh)
실행 환경         HDP Sandbox
```

Spark는 감성 점수 계산, 날짜 기준 조인, 상관계수 산출에 쓰고
Hive는 섹터별 집계와 날짜별 통계 쿼리에 쓴다.

---

## 파이프라인 구현 기획

```
① 뉴스 수집    src/ingest/collect_news.py    → data/raw/news/
② 주가 수집    src/ingest/collect_stock.py   → data/raw/stock/
③ HDFS 적재    hdfs dfs -put
④ Spark 전처리 src/pipeline/process.py       → 감성 점수 계산, 수익률 계산, 날짜 조인
⑤ Hive 집계    src/pipeline/query.hql        → 섹터별 통계, 상관관계
⑥ 시각화       src/analyze/dashboard.py      → Streamlit 대시보드
```

전체 파이프라인은 `run_pipeline.sh` 한 번으로 실행.

```bash
bash run_pipeline.sh
```

## 프로젝트 구조

```
news-stock-correlation/
├── README.md
├── run_pipeline.sh
├── data/
│   └── README.md              # 데이터 출처 및 스키마
├── src/
│   ├── ingest/
│   │   ├── collect_news.py    # BigKinds API 뉴스 수집
│   │   └── collect_stock.py   # KOSPI 주가 수집
│   ├── pipeline/
│   │   ├── process.py         # Spark 전처리 및 감성 점수 계산
│   │   ├── load.hql           # Hive 테이블 생성
│   │   └── query.hql          # Hive 분석 쿼리
│   └── analyze/
│       └── dashboard.py       # Streamlit 시각화
└── .gitignore
```

---

## AI 도구 사용

- Claude: README 작성 보조, 경제 뉴스 API 정보, 기획 구체화 보조

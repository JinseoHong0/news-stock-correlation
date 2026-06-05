echo "== Calling List(1/4) =="
python3.6 src/ingest/collect_stock_list.py

echo "== KOSPI (2/4) =="
python3.6 src/ingest/collect_kospi_ticker.py

echo "== KOSDAQ (3/4) =="
python3.6 src/ingest/collect_kosdaq_ticker.py

echo "== Collect News(4/4) =="
python3.6 src/ingest/collect_news.py

du -sh data/raw/

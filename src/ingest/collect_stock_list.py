import FinanceDataReader as fdr

# 시총 기준 KOSPI 전체 리스트
df_kospi = fdr.StockListing('KOSPI') 
# 코스피 종목별 상세 정보
df_kospi_desc = fdr.StockListing('KOSPI-DESC')    

df_kospi.to_csv('data/raw/stock_list/KOSPI_list.csv', index=False, encoding='utf-8-sig')
df_kospi_desc.to_csv('data/raw/stock_list/KOSPI_DESC.csv', index=False, encoding='utf-8-sig')

# 시총 기준 KOSDAQ 전체 리스트
df_kosdaq = fdr.StockListing('KOSDAQ') 
# 코스닥 종목별 상세 정보
df_kosdaq_desc = fdr.StockListing('KOSDAQ-DESC')    

df_kosdaq.to_csv('data/raw/stock_list/KOSDAQ_list.csv', index=False, encoding='utf-8-sig')
df_kosdaq_desc.to_csv('data/raw/stock_list/KOSDAQ_DESC.csv', index=False, encoding='utf-8-sig')

#코스피 코스닥 지수 데이터 수집
Kospi = fdr.DataReader('KS11', '2016-01-01', '2020-12-31')
Kospi.index.name = 'Date'
Kospi = Kospi.reset_index() 

Kosdaq = fdr.DataReader('KQ11', '2016-01-01', '2020-12-31')
Kosdaq.index.name = 'Date'
Kosdaq = Kosdaq.reset_index()

Kospi.to_csv('data/raw/index/KOSPI_16to20.csv', index=False, encoding='utf-8-sig')
Kosdaq.to_csv('data/raw/index/KOSDAQ_16to20.csv', index=False, encoding='utf-8-sig')

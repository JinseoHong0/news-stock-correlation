import FinanceDataReader as fdr
import pandas as pd
import os

START      = '2016-01-01'
END        = '2020-12-31'
OUT_DIR    = 'data/raw/kospi_ticker'

tickers = pd.read_csv('data/raw/stock_list/KOSPI_2016.csv', dtype={'Code': str})

for i, row in tickers.iterrows():
    code = row['Code']
    fpath = os.path.join(OUT_DIR, code + '.csv')

    try:
        df = fdr.DataReader(code, START, END)
        if len(df) == 0:
            continue
        df['Code'] = code
        df.to_csv(fpath, encoding='utf-8-sig')
        print(f"Successfully collected data for {code}")    
    except Exception as e:
        print(f"Error for {code}: {e}")
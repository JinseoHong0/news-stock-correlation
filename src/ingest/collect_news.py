import pandas as pd
from datasets import load_dataset

ds = load_dataset("klue", "ynat")

df = pd.concat([ds['train'].to_pandas(), ds['validation'].to_pandas()], ignore_index=True)

label_names = ds['train'].features['label'].names
df['category'] = df['label'].map(lambda x: label_names[x])

df_out = df[['date', 'title', 'category']]

df_out.to_csv('data/raw/news/klue_ynat_raw.csv', index=False, encoding='utf-8-sig')

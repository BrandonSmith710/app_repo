import pandas as pd
import numpy as np
import os
import pickle, re

path = os.path.join(os.getcwd(), 'data.csv')
df1 = pd.read_csv(path)

my_ex_query = df1.iloc[15]['id']
df = df1[['id', 'name', 'acousticness', 'danceability', 'energy', 'loudness',
                 'mode', 'liveness', 'valence', 'tempo', 'duration_ms']]
# df_copy = pd.DataFrame({x: df[x][:50000] for x in df.columns if not x == 'name'})

def clean_text(text):

  text = text.replace('\n', ' ')

  text = re.sub('[^a-zA-Z 0-9]', '', text)

  text = re.sub('[ ]{2, }', ' ', text)

  return text.lower().strip()

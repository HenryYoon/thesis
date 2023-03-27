import langid
from koalanlp import API
from koalanlp.Util import initialize, finalize
from koalanlp.proc import SentenceSplitter
from konoha import SentenceTokenizer
import sentence_splitter
import re
import warnings
from tqdm import tqdm
import pandas as pd


df['text'] = df['text'].str.replace(pat=r'\([^)]*\)', repl=r'', regex=True)
df['title'] = df['title'].str.replace(pat=r'\([^)]*\)', repl=r'', regex=True)

df['text'] = df['text'].str.replace(pat=r'\([^)]*\)', repl=r'', regex=True)
df['title'] = df['title'].str.replace(pat=r'\([^)]*\)', repl=r'', regex=True)


tqdm.pandas()
warnings.filterwarnings(action='ignore')

ko = pd.read_csv('./data/president_ko.csv')
us = pd.read_csv('./data/president_us.csv')
jp = pd.read_csv('./data/president_jp.csv')

ko['country'] = 'ko'
us['country'] = 'us'
jp['country'] = 'jp'

df = pd.concat([ko, us, jp], axis=0)
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['doc_id'] = [f'{i}_{j}_{k}' for i, j, k in zip(
    df['country'], df.index.to_list(), df['year'])]

df['country'] = [i[:2] for i in df['doc_id']]
df['country'] = df['country'].replace(
    {'ko': 'Korea', 'us': 'U.S.A.', 'jp': 'Japan'})

df = df[['doc_id', 'date', 'year', 'country', 'president', 'title', 'text']]
df = df.reset_index(drop=True)


initialize(HNN='LATEST')

splitter = SentenceSplitter(API.HNN)

tqdm.pandas()
warnings.filterwarnings(action='ignore')

splitter_en = sentence_splitter.SentenceSplitter(language='en')
tokenizer = SentenceTokenizer()

ko = pd.read_csv('../data/president_kr_v1.csv')
us = pd.read_csv('../data/president_us_v1.csv')
jp = pd.read_csv('../data/president_jp_v1.csv')

ko['sent'] = ko['text'].progress_apply(splitter)
us['sent'] = us['text'].progress_apply(splitter_en.split)
jp['sent'] = jp['text'].progress_apply(tokenizer.tokenize)

finalize()


ko['country'] = 'ko'
us['country'] = 'us'
jp['country'] = 'jp'

df = pd.concat([ko, us, jp], axis=0)
df['doc_id'] = [f'{i}_{j}_{k}' for i, j, k in zip(
    df['country'], df.index.to_list(), df['year'])]

df['country'] = [i[:2] for i in df['doc_id']]
df['country'] = df['country'].replace(
    {'ko': 'Korea', 'us': 'America', 'jp': 'Japan'})

df = df[['doc_id', 'date', 'year', 'country',
         'president', 'title', 'text', 'sent']]
df = df.reset_index(drop=True)

keywords = [('북한', '北朝鮮', 'North Korea'), ('미사일', 'ミサイル', 'Missile'), ('금융위기', '金融危機', 'Recession'),
            ('멕시코', 'メキシコ', 'Mexico'), ('파나마', 'パナマ', 'Panama'), ('민주화', '民主化', 'Democratization')]

pres = []
lines = []
ids = []
year = []
keyword1 = []
country = []

for keyword in keywords:
    df_temp = df[df['text'].str.contains('|'.join(keyword), case=False)]
    for data in df_temp.itertuples():
        temp = [line for line in data.sent]
        temp = [sent for sent in temp if any(word in sent for word in keyword)]
        pres.extend([data.president] * len(temp))
        lines.extend(temp)
        ids.extend([data.doc_id] * len(temp))
        year.extend([data.year] * len(temp))
        keyword1.extend([keyword[2]] * len(temp))
        country.extend([data.country] * len(temp))

df1 = pd.DataFrame({'doc_id': ids, 'year': year, 'president': pres,
                   'country': country, 'sent': lines, 'keyword': keyword1})


tqdm.pandas()

df = pd.read_csv('./data/president.csv')
df = df.dropna(subset='text')
df['sent'] = df['text'].progress_apply(
    lambda x: re.split('(?<=[^0-9A-Z|Mrs|Mr])[\.\?\!\。]', x))


df['lang'] = df['text'].progress_apply(lambda x: langid.classify(x)[0])
df['lang'].value_counts()


idx1 = df[df['title'].str.contains(
    'News Conference|기자회견|기자와의|記者|Vice|Budget')].index
df = df.drop(index=idx1)

pres = ['Adlai Stevenson', 'Barry Goldwater', 'Hubert H. Humphrey', 'George McGovern', 'Walter F. Mondale',
        'Michael S. Dukakis', 'Robert Dole', 'Albert Gore, Jr.', 'John F. Kerry', 'John McCain', 'Mitt Romney']
idx2 = df.query("president.isin(@pres)").index
df = df.drop(index=idx2)

langs = ['ko', 'en', 'ja', 'zh']

df = df.query("lang.isin(@langs)")
df = df.reset_index(drop=True)

df.to_pickle('./data/president.pkl')
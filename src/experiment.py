import seaborn as sns
import numbers
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pandas as pd
from tqdm import tqdm
import warnings
import sys

warnings.filterwarnings(action='ignore')
tqdm.pandas()

df = pd.read_pickle('../data/filter_v2.pkl')


documents = [TaggedDocument(doc.lower(), [id])
             for id, doc in zip(df['doc_id'], df['trans'].str.lower())]
model = Doc2Vec(documents, vector_size=300, window=5, min_count=1, workers=4)

diff = pd.DataFrame()
full = pd.DataFrame()
for word in tqdm(df['keyword'].unique()):
    df_temp = df.query(f"keyword == '{word}'")[['doc_id', 'date']]

    sims = []
    for id in df_temp['doc_id']:
        topn = model.dv.most_similar(id, topn=sys.maxsize)
        # temp = [id1 for id1, score in topn if score >= 0.7 and id1[:2] != id[:2]]     if with different countries
        temp = [id1 for id1, score in topn if score >= 0.7]                             # if with same countries
        temp = [id1 for id1 in temp if id1 in df_temp['doc_id'].to_list()]
        sims.extend([(id, x) for x in temp])

    edge = pd.DataFrame(sims, columns=['id1', 'id2'])

    date_from = []
    date_to = []
    for data in edge.itertuples():
        date_from.append(df.query("doc_id == @data.id1")['date'].to_list()[0])
        date_to.append(df.query("doc_id == @data.id2")['date'].to_list()[0])

    edge['date_from'] = date_from
    edge['date_to'] = date_to

    v1 = []
    date = []
    keyword = []

    for data in edge.itertuples():
        date1 = data.date_from
        date2 = data.date_to
        if abs((date1 - date2).days) <= 30:
            if date1 > date2:
                v1.append((data.id2, data.id1))
                date.append((date2, date1))
            else:
                v1.append((data.id1, data.id2))
                date.append((date1, date2))

    edge = pd.DataFrame(v1, columns=['id_from', 'id_to'])
    dates = pd.DataFrame(date, columns=['date_from', 'date_to'])
    edge['keyword'] = [word] * len(edge)
    edge = pd.concat([edge, dates], axis=1)

    edge['country_from'] = [i[:2] for i in edge['id_from']]
    edge['country_to'] = [i[:2] for i in edge['id_to']]

    edge['country_from'] = edge['country_from'].replace(
        {'ko': 'Korea', 'us': 'U.S.A.', 'jp': 'Japan'})
    edge['country_to'] = edge['country_to'].replace(
        {'ko': 'Korea', 'us': 'U.S.A.', 'jp': 'Japan'})

    diff = pd.concat([diff, edge], axis=0)  # with different countries
    full = pd.concat([full, edge], axis=0)  # with same countries

diff['diff'] = diff['country_from'] != diff['country_to']

diff1 = diff[diff['diff']]
ids = list(set(diff1['id_from']) | set(diff1['id_to']))


def dummy_fun(doc):
    return doc


vectorizer = CountVectorizer(lowercase=False, tokenizer=dummy_fun)
name = vectorizer.get_feature_names_out()
X = vectorizer.fit_transform(df['token'].to_list())

X = np.array(X.toarray(), dtype=np.float64)
u, s, vh = svds(X, k=300)

vh1 = sparse.csr_matrix(vh)
sim = cosine_similarity(vh1.T, vh1.T)


sent_dict = pd.read_csv('../data/survey_lex.csv',
                        sep=',', names=['word', 'score'], )
sent_dict = {k: v for k, v in zip(sent_dict['word'], sent_dict['score'])}

# name = model.wv.key_to_index
name2idx = {k: v for v, k in enumerate(name)}
new2idx = {k: name2idx[k] for k in sent_dict.keys() if k in name}
idx2sent = {new2idx[k]: sent_dict[k] for k in sent_dict.keys() if k in name}

score = np.zeros(len(name))
np.put(score, list(idx2sent.keys()), list(idx2sent.values()))

sim = sim * score
lexicon = {k: v for k, v in zip(name, sim.sum(axis=1))}
lexicon.update(sent_dict)


def sentiment(sent):
    for x in sent:
        if x in lexicon.keys():
            result = [lexicon.get(x, x) for x in sent]
            result = [x for x in result if isinstance(x, numbers.Number)]
            result = np.array(result)
            return np.mean(result)
        else:
            pass


df['score'] = df['token'].apply(sentiment)
df1 = df.query("doc_id.isin(@ids)")

plot = df1.query("keyword == 'North Korea'")
plot['wrap'] = plot['text'].str.wrap(60)
plot['wrap'] = plot['wrap'].apply(lambda x: x.replace('\n', '<br>'))

plot['stance'] = ['Negative' if x <= -0.01 else 'Neutral' if -
                  0.01 < x < 0.01 else 'Positive' for x in plot['score']]

pd.options.plotting.backend = 'plotly'
fig = plot.plot(x="date", y="country", kind="scatter", color='stance', facet_col='keyword', facet_col_wrap=2, hover_data=[
                'doc_id', 'wrap', 'score'], color_discrete_map={"Negative": "red", "Neutral": "green", "Positive": "blue"},)

annotations = []
for i, word in enumerate(plot['keyword'].unique()):
    for row in diff.query("keyword == @word").itertuples():
        annotations.append(dict(x=row.date_to, y=row.country_to, xref=f'x{i+1}', yref=f'y{i+1}',
                                ax=row.date_from, ay=row.country_from, axref=f'x{i+1}', ayref=f'y{i+1}',
                                showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1))
fig.update_layout(annotations=annotations)

fig.update_traces(marker_size=10)
fig.update_layout(width=1200, height=600)
fig.update_yaxes(tickangle=0)

fig.show()

# visualize edge density (interaction)

plot['date'] = plot['date'].dt.strftime('%Y-%m-%d')

diff1['date_from'] = diff1['date_from'].dt.strftime('%Y-%m-%d')
diff1['date_to'] = diff1['date_to'].dt.strftime('%Y-%m-%d')


sns.set_style('darkgrid')

diff1 = diff[diff['diff']]

pd.options.plotting.backend = 'plotly'

plot1 = pd.crosstab(diff.year, diff.keyword, margins=True)
plot1 = plot1.drop(['All'], axis=0)
plot2 = pd.crosstab(diff1.year, diff1.keyword, margins=True)
plot2 = plot2.drop(['All'], axis=0)

plot = plot2.div(plot1['All'], axis=0).fillna(0)
plot.plot()

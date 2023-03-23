from tqdm import tqdm
import pickle
from tokenizer import *


def replace_edge(edge, df):
    v1 = []
    date = []
    for i in tqdm(edge):
        date1 = df.loc[i[0][0], 'date']
        date2 = df.loc[i[1][0], 'date']

        if date1 > date2:
            v1.append((i[1][1], i[0][1]))
            date.append((date2, date1))
        else:
            v1.append((i[0][1], i[1][1]))
            date.append((date1, date2))
    return v1, date


def save_pickle(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(file=f, obj=obj)


def load_pickle(path):
    with open(path, 'rb') as f:
        obj = pickle.load(f)
    return obj


def extract_noun(x):
    if x[1] == 'kr':
        noun = tokenizer_ko(x[0])
    elif x[1] == 'en':
        noun = tokenizer_us(x[0])
    elif x[1] == 'ja':
        noun = tokenizer_jp(x[0])
    else:
        noun = None
    return noun


def translate_text(text):

    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    result = translate_client.translate(text, target_language='en')
    return result['translatedText']

from tqdm import tqdm
import pickle
from tokenizer import *

import json
import urllib.request
from sklearn.feature_extraction.text import TfidfVectorizer

#Naver Papago API info
client_id = "ysh5co9znp"
client_secret = "zfH5pZLG4ttOUGCeydpr4NKPVoFJA8B5NOdkHkhm"
client_header = {"X-NCP-APIGW-API-KEY-ID":client_id,
                    "X-NCP-APIGW-API-KEY":client_secret}

def replace_edge(edge, df):
    v1 = []; date=[]
    for i in tqdm(edge):
        date1 = df.loc[i[0][0],'date']
        date2 = df.loc[i[1][0],'date']

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
    with open(path,'rb') as f:
        obj = pickle.load(f)
    return obj


def detect_lang(text):
    encQuery = urllib.parse.quote(text)
    data = "query=" + encQuery
    url = "https://naveropenapi.apigw.ntruss.com/langs/v1/dect"

    request = urllib.request.Request(url, headers=client_header)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if (rescode==200):
        response_body = response.read()
        response_body = response_body.decode('utf-8')
        response_body = json.loads(response_body)
        return response_body['langCode']
    else:
        print("Error Code:" + rescode)


def translate(text, src):
    encText = urllib.parse.quote(text)
    data = f"source={src}&target=en&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"

    request = urllib.request.Request(url, headers=client_header)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if (rescode==200):
        response_body = response.read()
        response_body = response_body.decode('utf-8')
        response_body = json.loads(response_body)
        response_body = response_body['message']['result']['translatedText']
        return response_body
    else:
        print("Error Code:" + rescode)


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
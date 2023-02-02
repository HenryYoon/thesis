from konlpy.tag import Mecab
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from fugashi import Tagger
from nltk.tokenize import RegexpTokenizer
import re
import string


def tokenizer_ko(x):
    tok = Mecab(dicpath="c:/mecab/mecab-ko-dic")
    # tok = Mecab()
    # tok = Kkma()
    p = re.compile(r'\w')
    # p1 = re.compile(r'\b6·25\b|\b5.18\b|\b6.10\b|\b6.25\b|\b8.25\b|\b6.15\b|\b6,29\b|\b6.29\b')

    x = [i for i in tok.morphs(x) if p.match(i)]
    # x = [i for i in tok.morphs(x) if p1.match(i)]
    # x = [i for i in x if p1.match(i)]
    x = [i for i in x if len(i) > 1]
    return x


def tokenizer_us(x):
    wnl = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(f'\s+|[{string.punctuation}]', gaps=True)
    stop = list(stopwords.words('english')) + ['mr','mrs','ms','q','s']
    # p = re.compile(r'\w+')
    p = re.compile(r'\D')
    
    mwe = [('North', 'Korea'), ('North', 'Korean'), ('six-party', 'talk'), ('six-party', 'talks'), ('Korean', 'War'), \
            ('korean', 'war'), ('Kim','Il','Sung'), ('Kim','Jong','Il'), ('Kim', 'Jong','Un'), \
            ('Kim','Il-Sung'), ('Kim','Jong-Il'), ('Kim', 'Jong-Un')]
    tok = nltk.tokenize.MWETokenizer(mwe, separator=' ')

    pos = ['NOUN', 'VERB', 'ADJ', 'ADV']
    p2p = {'ADJ':'a', 'VERB':'v', 'NOUN':'n', 'ADV':'r'}

    x = [i for i in tokenizer.tokenize(x) if not i.lower() in stop]
    x = [i for i in tok.tokenize(x) if p.match(i)]
    x = [i for i in nltk.pos_tag(x, tagset='universal') if any(p in i[1] for p in pos)]
    
    x = [wnl.lemmatize(i[0], pos=p2p[i[1]]) for i in x]
    x = [i for i in x if len(i) > 1]
    return x


def tokenizer_jp(x):
    tagger = Tagger('iwanami')
    # pos = ['名詞','副詞','形容詞']
    # p = re.compile(r'\w')
    p1 = re.compile(r'\D')

    x = tagger(x)
    x = [word.surface for word in x if p1.match(word.surface)]
    # x = [i for i in x ]
    # x = [i for i in x if p1.match(i)]
    # x = [word.surface for word in x if any(x in word.feature[0] for x in pos)]
    x = [i for i in x if len(i) > 1]
    return x


# wordvec = {}
# for i, word in enumerate(vectorizer.get_feature_names_out()):
#     wordvec[word] = vh[:,i]
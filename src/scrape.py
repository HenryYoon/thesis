import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm, trange
import time


def scrape_ko():
    root_url = "https://www.pa.go.kr/research/contents/speech/index.jsp"

    param = {"pageUnit": 100, 'mediaType': 'doc'}
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

    res1 = requests.get(root_url, headers=header, params=param)
    results = BeautifulSoup(res1.text, 'html.parser')

    total_page = results.select_one(
        'div[class="board-count left"] p strong').get_text()
    total_page = int(total_page.strip().replace(',', ''))
    total_page = total_page // 100 + 1

    res1.close()

    address = []
    for i in trange(1, total_page+1):
        param['pageIndex'] = i
        res2 = requests.get(root_url, params=param, headers=header)
        result = BeautifulSoup(res2.text, 'html.parser')

        ref = [i.find('a').get('href')
               for i in result.findAll('td', class_='subject')]
        res2.close()

        for link in ref:
            res3 = requests.get(root_url + link, headers=header)
            results = BeautifulSoup(res3.text, 'html.parser')

            a = [i.text for i in results.find_all('td')]
            dict = {'title': a[0], 'date': a[1],
                    'president': a[2], 'category': a[4], 'text': a[6]}
            address.append(dict)
            res3.close()

        time.sleep(1)

    print('-' * 18)
    df = pd.DataFrame.from_dict(address, orient='columns')
    df.to_csv('./data/president_ko1.csv', index=False)


def scrape_us():
    root_url = "https://www.presidency.ucsb.edu"
    search = '/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=07-14-1948&to%5Bdate%5D=03-30-2022&person2=&category2%5B%5D=8&items_per_page=100'
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}

    total_page = 14506 // 100 + 1

    presidents = []
    dates = []
    titles = []
    texts = []

    for i in trange(total_page):
        url = root_url + search + f"&page={i}"

        res1 = requests.get(url, headers=header)
        result1 = BeautifulSoup(res1.text, 'html.parser')

        ref = [i.find('a').get('href') for i in result1.findAll(
            'td', class_='views-field views-field-title')]
        res1.close()

        for url in ref:
            res2 = requests.get(root_url + url, headers=header)
            result2 = BeautifulSoup(res2.text, 'html.parser')

            president = result2.find('h3').text
            date = result2.find(
                'span', class_='date-display-single').get('content')
            title = result2.find('div', class_='field-ds-doc-title').text
            text = result2.find('div', class_='field-docs-content').text

            presidents.append(president)
            dates.append(date)
            titles.append(title)
            texts.append(text)

        time.sleep(1)

    print('-' * 18)
    df = pd.DataFrame({'president': presidents, 'date': dates,
                      'title': titles, 'text': texts})
    df.to_csv('./data/president_us1.csv', index=False)


def scrape_jp():
    url = "https://worldjpn.net/documents/indices/exdpm/iindex.html"
    root = 'https://worldjpn.net/documents'

    table = pd.read_html(url, encoding='utf-8')

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tb = soup.find_all('table')

    texts = []
    for tr in tqdm(tb[2].findAll("tr")[1:]):
        link = tr.find('a')['href']
        res1 = requests.get(root+link[5:])
        soup = BeautifulSoup(res1.text, 'html.parser')
        text = ' '.join([t.text.encode('latin1', 'ignore').decode(
            'utf-8', 'ignore').strip() for t in soup.findAll('p')[1:]])
        texts.append(text)
        time.sleep(1)

    ex = pd.DataFrame(
        {'date': table[2]['年 月 日'], 'title': table[2]['演　説　名'], 'text': texts})
    ex['date'] = ex['date'].replace({'1970月9月21日': '1970年9月21日', '1972年9年11日': '1972年9月11日', '1973月10月2日': '1973年10月2日', '1977年8年18日': '1977年8月18日', '1987月1月15日': '1987年1月15日',
                                    '1994月9月20日': '1994年9月20日', '2002年4年21日': '2002年4月21日', '2007年1年1月': '2007年1月1日', '2007年8年22日': '2007年8月22日', '2008年6年13日': '2008年6月13日', '202年6月22日': '2022年6月22日'})

    def date_manipulate(x):
        try:
            x = pd.to_datetime(x, format='%Y年%m月%d日')
        except ValueError:
            x = pd.to_datetime(x, format='%Y年%m月')
        return x
    ex['date'] = ex['date'].apply(date_manipulate)
    ex['date'] = ex['date'].dt.strftime('%Y-%m-%d')

    url1 = 'https://worldjpn.net/documents/indices/pm'
    url2 = 'https://worldjpn.net/documents/texts/pm'

    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"}

    texts = []
    titles = []
    dates = []
    for i in trange(48, 101):
        res1 = requests.get(url1+f'/{i}.html', headers=header)
        result1 = BeautifulSoup(res1.text, 'html.parser')
        ref = [i.get('href') for i in result1.findAll('a')]
        titles.extend([i.text.encode('latin1', 'ignore').decode(
            'utf-8', 'ignore') for i in result1.findAll('a')])
        dates.extend([i.split('/')[4].split('.')[0] for i in ref])
        res1.close()

        for link in ref:
            res2 = requests.get(url2 + link[-18:], headers=header)
            result2 = BeautifulSoup(res2.text, 'html.parser')
            text = ' '.join([t.text.encode('latin1', 'ignore').decode(
                'utf-8', 'ignore') for t in result2.findAll('p')[1:]])
            texts.append(text)

        time.sleep(1)

    print('-' * 18)
    diet = pd.DataFrame({'date': dates, 'title': titles, 'text': texts})
    diet['date'] = pd.to_datetime(
        diet['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    df = pd.concat([ex, diet], axis=0)
    df['date'] = pd.to_datetime(df['date'])

    df = df.set_index('date')
    df = df.loc['1948-07-14':'2022-03-30', :]

    df.loc['1948-03-10':'1948-10-15', 'president'] = '芦田均'
    df.loc['1948-10-15':'1954-12-10', 'president'] = '吉田茂'
    df.loc['1954-12-10':'1956-12-23', 'president'] = '鳩山一郎'
    df.loc['1956-12-23':'1957-02-25', 'president'] = '石橋湛山'
    df.loc['1957-02-25':'1960-07-19', 'president'] = '岸信介'

    df.loc['1960-07-19':'1964-11-09', 'president'] = '池田勇人'
    df.loc['1964-11-09':'1972-07-07', 'president'] = '佐藤榮作'
    df.loc['1972-07-07':'1974-12-09', 'president'] = '田中角榮'
    df.loc['1974-12-09':'1976-12-24', 'president'] = '三木武夫'

    df.loc['1976-12-24':'1978-12-07', 'president'] = '福田赳夫'
    df.loc['1978-12-07':'1980-06-12', 'president'] = '大平正芳'
    df.loc['1980-06-12':'1980-07-17', 'president'] = '伊東正義'
    df.loc['1980-07-17':'1982-11-27', 'president'] = '鈴木善幸'

    df.loc['1982-11-27':'1987-11-06', 'president'] = '中曾根康弘'
    df.loc['1987-11-06':'1989-06-03', 'president'] = '竹下登'
    df.loc['1989-06-03':'1989-08-10', 'president'] = '宇野宗佑'
    df.loc['1989-08-10':'1991-11-05', 'president'] = '海部俊樹'

    df.loc['1991-11-05':'1993-08-09', 'president'] = '宮澤喜一'
    df.loc['1993-08-09':'1994-04-28', 'president'] = '細川護熙'
    df.loc['1994-04-28':'1994-06-30', 'president'] = '村山富市'
    df.loc['1994-06-30':'1996-01-11', 'president'] = '村山富市'
    df.loc['1996-01-11':'1998-07-30', 'president'] = '橋本龍太郎'

    df.loc['1998-07-30':'2000-04-15', 'president'] = '小渕恵三'
    df.loc['2000-04-15':'2001-04-26', 'president'] = '森喜朗'
    df.loc['2001-04-26':'2006-09-26', 'president'] = '小泉純一郎'
    df.loc['2006-09-26':'2007-09-26', 'president'] = '安倍晋三'

    df.loc['2007-09-26':'2008-09-24', 'president'] = '福田康夫'
    df.loc['2008-09-24':'2009-09-16', 'president'] = '麻生太郎'
    df.loc['2009-09-16':'2010-06-08', 'president'] = '鳩山由紀夫'
    df.loc['2010-06-08':'2011-09-02', 'president'] = '菅直人'

    df.loc['2011-09-02':'2012-12-26', 'president'] = '野田佳彦'
    df.loc['2012-12-26':'2020-09-16', 'president'] = '安倍晋三'
    df.loc['2020-09-16':'2021-10-04', 'president'] = '菅義偉'
    df.loc['2021-10-04':'2022-03-30', 'president'] = '岸田文雄'
    df = df.reset_index()

    df.to_csv('./data/president_jp1.csv', index=False)

import time
from selenium import webdriver
import bs4
import urllib.request 
import re
import pandas as pd


def get_news(symbol):
    driver = webdriver.Chrome('C:/Users/andre/Downloads/chromedriver_win32/chromedriver.exe')  # Optional argument, if not specified will search path.
    driver.get('https://www.otcmarkets.com/stock/'+symbol+'/news');
    time.sleep(5) # Let the user actually see something!
    page=driver.page_source
    soup = bs4.BeautifulSoup(page,'html.parser')
    newsTable= soup.find_all("table", {"id":"newsTable"})
    newsLink =[]
    for item  in newsTable:
        for link in item.find_all('a'):
            l= link.get('href')
            if l.find('stock')>-1:
                newsLink.append('https://www.otcmarkets.com'+l)
    return newsLink




def sentimental_analysis(url): 
    page=urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(page,'html.parser')
    news= soup.find_all("div", {"class":"newsDetail"})
    for c in news:
        text=c.text
    m = re.search('(About.*)', text)
    start=m.start(1)
    text=text.replace(text[start:],'')
    text=re.sub(r"http://[a-z]+.[a-z]+.[a-z]+", '', text)
    text=re.sub(r"www.[a-z]+.[a-z]+", '', text)
    text=re.sub(r"[''/:();&\"]", ' ', text)
    text=re.sub(r"(\. )", ' ', text)
    text=re.sub(r"(, )", ' ', text)
    text=re.sub(r",", '', text)
    text=text.split(' ')
    for i in range(0,len(text)):
        text[i]=re.sub(r"[\n\r\xa0]", '', text[i])
        text[i]=text[i].lower()
        if text[i] in ('on','in','of','to','at','a','an','the','with','and','as','for','or','by','-','from'):
            text[i]=''
    while '' in text:
        text.remove('')    
    ##print(text)

    postive=0
    negative=0
    for word in text:
        if word in term:
            i = term.index(word)
            postive+=pos[i]
            negative+=neg[i]
    return postive-negative
    
    


def calculate_avg_score(symbol):
    score=0
    link=get_news(symbol)
    for l in link:
        s= sentimental_analysis(l)
        score+=s
    if len(l)>0:
        avg=score/len(l)
    else:
        avg=0
    return(avg)


## term list
df=pd.read_table("C:/Users/andre/Downloads/SentiWordNet_3.0.0_20130122.txt",sep='\t')
s = df['SynsetTerms'].str.split('|').apply(pd.Series, 1).stack()
s.index = s.index.droplevel(-1)
s.name = 'SynsetTerms'
del df['SynsetTerms']
df=df.join(s)
pos=list(df['PosScore'])
neg=list(df['NegScore'])
term=list(df['SynsetTerms'])
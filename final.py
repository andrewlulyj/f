import time
from selenium import webdriver
import bs4
import urllib.request 
import re
import pandas as pd

def get_symbol_list():
    url ='https://github.com/andrewlulyj/f/blob/master/Stock_Screener.csv'
    page=urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(page,'html.parser')
    s=soup.text
    b = re.search('(Symbol)', s)
    e = re.search('(Copy lines)', s)
    start=b.start(1)
    end=e.start(1)
    s=s[start:end]
    s=s.split('\n\n\n\n')
    for i in range(0,len(s)):
       s[i]=re.sub(r"[\n\r]", '', s[i])
    s=s[1:len(s)-2]
    return s


def get_news(symbol):
    driver =  webdriver.Chrome('C:/Users/andre/Downloads/chromedriver_win32/chromedriver.exe')  # Optional argument, if not specified will search path.
    driver.get('https://www.otcmarkets.com/stock/'+symbol+'/news');
    ##time.sleep(2) 
    page=driver.page_source
    soup = bs4.BeautifulSoup(page,'html.parser')
    driver.quit()
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
    if m:
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
    if len(link)>0:
        avg=round(score/len(link),3)
    else:
        avg=0
    return(symbol,avg)


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

symbol_list =get_symbol_list()
symbol_list =symbol_list[111:]
stock=[]
score=[]
for i in symbol_list:
   symbol,avg= calculate_avg_score(i)
   stock.append(symbol)
   score.append(avg)
   print(i)
d = {'Symbol': stock, 'Score':score }
df=pd.DataFrame(d)
df.to_csv('score.csv')
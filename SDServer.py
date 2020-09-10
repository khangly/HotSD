#!/usr/bin/python3
import time
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import mysql.connector

LAST_LOCATION = '/home/k/kh/khangly/sd/last.txt'

def read_last():
    param = dict()
    with open(LAST_LOCATION, 'r') as f:
        param['thread'] = int(f.readline())
        param['post'] = int(f.readline())
        param['threadrate'] = int(f.readline())
    return param


def write_last(param):
    with open(LAST_LOCATION, 'w') as f:
        f.write(str(param['thread']) + '\n')
        f.write(str(param['post']) + '\n')
        f.write(str(param['threadrate']) + '\n')


def make_connection():
    return mysql.connector.connect(
      host="mysql",
      user="khangly",
      passwd="91FEyhBOOrFIhzba3TVANijH",
      database="khangly"
    )


#   Process Thread and return the ThreadID
def process_thread(bit, cursor):
    thread = int(bit['id'][7:])
    a_tag = bit.a.find_next('a')
    url = a_tag['href']
    item = a_tag.getText()
    with urllib.request.urlopen('https://slickdeals.net' + url) as request:
        content = BeautifulSoup(request.read(), 'lxml').find("div", class_="threadText").getText()
    insert_query = "INSERT IGNORE INTO Threads (ThreadID, URL, Item, Content, Created) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (thread, url, item, content, time.time()))
    print(item)
    return thread


#   Process ThreadRate and return the ThreadRateID
def process_threadrate(bit, cursor):
    threadrate = int(bit['id'][11:])
    url = bit.a['href']
    thread = int(url[3:url.find('-')])
    info = bit.span.getText().split(', ')
    replies = int(info[1][0:info[1].find(' ')])
    views = int(info[2][0:info[2].find(' ')])
    scores = int(info[3][0:info[3].find(' ')])
    insert_query = "INSERT IGNORE INTO ThreadRates VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (threadrate, thread, scores, replies, views, time.time()))
    return threadrate


#   Process Post and return the PostID
def process_post(bit, cursor):
    post = int(bit['id'][5:])
    url = bit.a.find_next('a')['href']
    thread = int(url[3:url.find('-')])
    info = bit.span.find_next('span').getText().split(', ')
    replies = int(info[0][0:info[0].find(' ')])
    views = int(info[1][0:info[1].find(' ')])
    scores = int(info[2][0:info[2].find(' ')])
    content = bit.p.getText()
    insert_query = "INSERT IGNORE INTO Posts VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (post, thread, scores, replies, views, content, time.time()))
    return post


#   Which to process
def process(bit, cursor, param):
    if bit['id'].startswith('thread_'):
        param['thread'] = max(param['thread'], process_thread(bit, cursor))
    elif bit['id'].startswith('threadrate_'):
        param['threadrate'] = max(param['threadrate'], process_threadrate(bit, cursor))
    else:
        param['post'] = max(param['post'], process_post(bit, cursor))


def fetch():
    param = read_last()
    query_string = urllib.parse.urlencode(param)
    spy = 'https://slickdeals.net/live/spy.php?' + query_string
    database = make_connection()
    cursor = database.cursor()
    with urllib.request.urlopen(spy) as request:
        soup = BeautifulSoup(request.read(), 'lxml')
    bits = soup.find_all('htmlbit')
    print("Len of bits:", len(bits))
    for i in range(len(bits) - 1, -1, -1):
        process(bits[i], cursor, param)
    database.commit()
    cursor.close()
    database.close()
    write_last(param)


fetch()

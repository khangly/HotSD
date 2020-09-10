import heapq
# import daemon
import time
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import mysql.connector

KEEP_LIVE = 12*60*60
DELAY = 1.5
UPVOTE_RATE_PER_HOUR = 5
VIEW_RATE_PER_MINUTE = 30

mydb = mysql.connector.connect(
  host="mysql",
  user="khangly",
  passwd="91FEyhBOOrFIhzba3TVANijH",
  database="khangly"
)

mycursor = mydb.cursor()


class Item:

    def __init__(self, deal_num, url, name):
        self.deal_num = deal_num
        self.url = url
        self.name = name
        self.created = time.time()
        self.ratings = list()
        self.cancels = 0
        self.price_mistakes = 0
        sql_insert_query = "REPLACE INTO Deals VALUES (%s, %s, %s, %s, %s, %s)"
        insert_tuple = (deal_num, url, name, self.created, 0, 0)
        mycursor.execute(sql_insert_query, insert_tuple)
        mycursor.execute("CREATE TABLE IF NOT EXISTS `" + str(deal_num) + "` (Time INT UNSIGNED PRIMARY KEY, Ratings SMALLINT, Replies SMALLINT UNSIGNED, Views MEDIUMINT UNSIGNED)")
        mydb.commit()

    def update_rating(self, upvotes, replies, views):
        insert_tuple = (time.time(), upvotes, replies, views)
        self.ratings.append(insert_tuple)
        sql_insert_query = "REPLACE INTO `" + str(self.deal_num) + "` VALUES (%s, %s, %s, %s)"
        mycursor.execute(sql_insert_query, insert_tuple)
        life_time = insert_tuple[0] - self.created
        if life_time and upvotes * 3600 / life_time > UPVOTE_RATE_PER_HOUR and views * 60 / life_time > VIEW_RATE_PER_MINUTE:
            sql_insert_query = "INSERT IGNORE INTO PM (ID) VALUES " + str(self.deal_num)
            mycursor.execute(sql_insert_query)
        mydb.commit()

    def update_cancels(self):
        self.cancels += 1
        sql_update_query = "UPDATE Deals SET Cancels = %s WHERE ID = %s"
        mycursor.execute(sql_update_query, (self.cancels, self.deal_num))
        if self.ratings and self.ratings[-1][1] > 1:
            sql_insert_query = "INSERT IGNORE INTO PM (ID) VALUES " + str(self.deal_num)
            mycursor.execute(sql_insert_query)
        mydb.commit()

    def update_price_mistakes(self):
        self.price_mistakes += 1
        sql_update_query = "UPDATE Deals SET Mistakes = %s WHERE ID = %s"
        mycursor.execute(sql_update_query, (self.price_mistakes, self.deal_num))
        if self.ratings and self.ratings[-1][1] > 0:
            sql_insert_query = "INSERT IGNORE INTO PM (ID) VALUES " + str(self.deal_num)
            mycursor.execute(sql_insert_query)
        mydb.commit()


#def


def fetch():
    items = dict()
    hq = list()
    param = {"thread": 1, "post": 1, "threadrate": 1, "time": int(time.time()), 'maxitems': 20}
    spy = 'https://slickdeals.net/live/spy.php'
    while True:
        try:
            html = urllib.request.urlopen(spy).read()
            soup = BeautifulSoup(html, 'lxml')
            bits = soup.find_all('htmlbit')
            # print("Len of bits:", len(bits))
            for i in range(len(bits) - 1, -1, -1):
                piece = bits[i]
                identifier = piece['id']
                a = piece.a
                if not identifier.startswith('threadrate_'):
                    a = piece.a.find_next('a')
                url = a['href']
                name = str(a.string)
                if identifier.startswith('thread_'):
                    deal_num = int(identifier[7:])
                    if param['thread'] < deal_num:
                        param['thread'] = deal_num
                    if deal_num not in items:
                        items[deal_num] = Item(deal_num, url, name)
                        heapq.heappush(hq, deal_num)
                        if name.find("pric") != -1 and name.find("mistake") != -1:
                            items[deal_num].update_price_mistakes()
                        try:
                            deal_content = BeautifulSoup(urllib.request.urlopen(spy).read(), 'lxml').find("div", class_="threadText").getText()
                            if deal_content.find("pric") != -1 and deal_content.find("mistake") != -1:
                                items[deal_num].update_price_mistakes()
                        except urllib.error.URLError:
                            pass
                        print(name)
                else:
                    if identifier.startswith('threadrate_'):
                        num = int(identifier[11:])
                        if param['threadrate'] < num:
                            param['threadrate'] = num
                    else:
                        num = int(identifier[5:])
                        if param['post'] < num:
                            param['post'] = num
                    deal_num = int(url[3:url.find('-')])
                    if deal_num in items:
                        index = 0
                        if identifier.startswith('threadrate_'):
                            info = piece.span.getText().split(', ')
                            index = 1
                        else:
                            info = piece.span.find_next('span').getText().split(', ')
                            p = str(piece.p.string)
                            if p.find("cancel") != -1:
                                items[deal_num].update_cancels()
                            if p.find("pric") != -1 and p.find("mistake") != -1:
                                items[deal_num].update_price_mistakes()
                        replies = int(info[index][0:info[index].find(' ')])
                        views = int(info[index + 1][0:info[index + 1].find(' ')])
                        upvotes = int(info[index + 2][0:info[index + 2].find(' ')])
                        items[deal_num].update_rating(upvotes, replies, views)
                        if time.time() - items[deal_num].created > KEEP_LIVE:
                            while hq and hq[0] <= deal_num:
                                items.pop(heapq.heappop(hq))
            query_string = urllib.parse.urlencode(param)
            spy = 'https://slickdeals.net/live/spy.php?' + query_string
            time.sleep(DELAY)
        except urllib.error.URLError:
            time.sleep(DELAY)


fetch()

#-*- coding:utf8 -*-

import requests
#import MySQLdb
from bs4 import BeautifulSoup
import re
import time

def get_url(url):
	r = requests.get(url);
	c = r.text;
	return c;

def parse_zbook():
	#c = get_url("http://t2.bookdna.cn:8088");
	c = get_url("https://www.amazon.cn/b/ref=sa_menu_kindle_l3_b1875254071?ie=UTF8&node=1875254071");
	soup = BeautifulSoup(c,'lxml');
	a = soup.body.find_all(href=re.compile('^"/dp/*"'));
	m = [];
	for i in a:
		m.append(i['href']);
	m = sorted(set(m),key=m.index);
	return m;

def parse_one(l):
	book = {};
	book['dp'] = l;
	c = get_url("https://www.amazon.cn"+book['dp']);
	soup = BeautifulSoup(c, 'lxml');
	book['image'] = soup.find('img',id='ebooksImgBlkFront')['src'];
	book['title'] = soup.find('span',id='ebooksProductTitle').text;
	book['author']= soup.find('span',class_='author notFaded').text;
	book['score'] = soup.find('span',id='acrPopover')['title'];
	book['price'] = soup.find('span',class_='a-size-base a-color-price a-color-price').text;
	book['date']  = time.strftime("%Y-%m-%d", time.localtime());
	return book;

'''def init_db():
	db = MySQLdb.connect("localhost","root","password","book_worm");
	cs = db.cursor();
	try:
		cs.execute("SELECT VERSION()");
	except Exception as e:
		raise
	else:
		return db;
	finally:
		pass;
'''

if __name__ == '__main__':
	l = parse_zbook();
	print("There are ",len(l)," books to parse");
	for x in l:
		print(parse_one(x));
#-*- coding:utf8 -*-

import requests
#import MySQLdb
from bs4 import BeautifulSoup

def get_url(url):
	r = requests.get(url);
	c = r.text;
	return c;

def parse_bdna():
	#c = get_url("http://t2.bookdna.cn:8088");
	c = get_url("http://39.108.80.238/");
	soup = BeautifulSoup(c,'lxml');
	s = soup.body.find_all('span');
	b = soup.body.find_all('b');
	a = soup.body.find_all('a');

	s.pop(0);
	
	a.pop(0);
	a.pop(0);
	a.pop(-1);


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
	parse_bdna();
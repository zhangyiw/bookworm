#-*- coding:utf8 -*-

import requests
import MySQLdb
from bs4 import BeautifulSoup
import re
import time

def get_url(url):
	headers = {
        'Host': 'www.amazon.cn',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.amazon.cn/',
        'Connection': 'keep-alive',
        'Cookie': '''session-id=459-0382294-8045805; session-id-time=2082729601l; ubid-acbcn=461-0072912-2527735; session-token=dFkVXRW7Ow39hcEkzlnaV0Wv6q0YVZYh3yXHinndOskS0BiGNcZ0XpNJ5BXTuAPnFE0cD18ft2Zb2vaAoYcv3EE5r3XkFs5ydWn9PMhCboO7befXNBGJ+tzMSzuZWtAjQptOoHJSCnWzuV2L98K0GTufP5GxY+2zYpMLpceL9bFnGfYGRI8KaQGageRaqeFw; csm-hit=s-923RXQ83V02BA5DA66R4|1519261746537; x-wl-uid=1jFFSZNo53sOykp3zxT1/FXm4aQQ2q4xsezsrDwkquYt/0EEVZHxZYqEo+KwIBMVVz82Z3TfP3k4=; s_nr=1518579715331-New; s_vnum=1950579693547%26vn%3D1; s_dslv=1518579715332'''
    };
	r = requests.get(url,headers=headers);
	print("Getting url:",url);
	c = r.text;
	print("Status code:",r.status_code);
#	with open('index.html','w') as fd:
#		fd.write(c);
	return c;

def parse_zbook():
	#c = get_url("http://t2.bookdna.cn:8088");
	c = get_url("https://www.amazon.cn/b/ref=sa_menu_kindle_l3_b1875254071?ie=UTF8&node=1875254071");
	soup = BeautifulSoup(c,'lxml');
	a = soup.body.find_all(href=re.compile('^/dp/*'));
	m = [];
	for i in a:
		m.append(i['href']);
	m = sorted(set(m),key=m.index);
	return m;

def parse_weekly():
	c = get_url('''https://www.amazon.cn/s/ref=s9_acsd_hps_bw_clnk_r?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&sort=popularity-rank&search-alias=digital-text&node=1852543071&pf_rd_m=A1AJ19PSB66TGU&pf_rd_s=merchandised-search-8&pf_rd_r=7X3PC84AJ9GMNZ12DVC0&pf_rd_t=101&pf_rd_p=2d85e30d-2e9e-416c-8325-cd9f23dc0653&pf_rd_i=1875254071''');
	soup = BeautifulSoup(c, 'lxml');
	b = soup.body.find_all(href=re.compile('^https://www.amazon.cn/dp/*'));
	w = [];
	if len(b) == 0:
		return w;
	for i in b:
		w.append(i['href'][21:35]);
	w = sorted(set(w),key=w.index);
	return w;


def parse_one(l):
	book = {};
	book['dp'] = l;
	print("Parse book:",l);
	c = get_url("https://www.amazon.cn"+book['dp']);
	soup = BeautifulSoup(c, 'lxml');
	book['image'] = soup.find('img',id='ebooksImgBlkFront')['src'];
	book['title'] = soup.find('span',id='ebooksProductTitle').text;
	book['author']= soup.find('span',class_='author notFaded').text.split('\n')[1];
	book['oprice']= re.findall(r"\d+\.?\d*",soup.find('span', \
		class_='a-color-base a-text-strike').text)[0];
	book['price'] = re.findall(r"\d+\.?\d*",soup.find('span', \
		class_='a-size-base a-color-price a-color-price').text)[0];
	book['date']  = time.strftime("%Y-%m-%d", time.localtime());
	book['score'] = 3.0;
	try:
		scor = re.findall(r"\d+\.?\d*",soup.find('span', \
		id='acrPopover')['title'])[0];
		book['score'] = float(scor);
	except Exception as e:
		print(e);
		print("Book:",l," does not have score.")
	print(book);
	return book;

def init_db():
	db = MySQLdb.connect(host="localhost",user="root",passwd="password",db="bookworm",charset="utf8");
	cs = db.cursor();
	try:
		cs.execute("SELECT VERSION()");
		data = cs.fetchone();
		print("Database Version: %s " % data);
	except Exception as e:
		print(e);
		print("Unable to connect to the MySQL Server.");
		return None;
	return db;

def check_book(book, db):
	cs = db.cursor();
	sql = "SELECT COUNT(1) FROM zbook WHERE BOOK_KID='"+book['dp']+"'";
	print("SQL: ",sql);
	try:
		cs.execute(sql);
		count = int(cs.fetchone());
		print("BOOK: ",book['dp']," nums: ",count);
		return count;
	except Exception as e:
		print(e);
		return 0;
		
def insert_book(book, db):
	cs = db.cursor();
	sql = "INSERT INTO zbook(book_kid, book_name, book_covr, author, hisl_price, hisl_date, curr_price, curr_date, score, oprice)"+\
	" VALUES('"+book['dp']+"','"+book['title']+"','"+book['image']+"','"+book['author']+"',"+book['price']+",'"+\
	book['date']+"',"+book['price']+",'"+book['date']+"',"+str(book['score'])+","+book['oprice']+")";
	print(sql);
	try:
		cs.execute(sql);
		db.commit();
		print("INSERT SUCCESSFULLY.");
	except Exception as e:
		print(e);
		db.rollback();

def merge_book(book, db):
	cs = db.cursor();
	sql1 = "SELECT hisl_price, hisl_date FROM zbook WHERE book_kid='"+book['dp']+"'";
	hisl_price = 10000.0;
	hisl_date = "2000-01-01";
	print(sql1);
	try:
		cs.execute(sql1);
		results = cs.fetchall();
		for row in results:
			hisl_price = float(row[0]);
			hisl_date = str(row[1]);
			print(hisl_date+" : "+str(hisl_price));
			break;

	except Exception as e:
		print(e);
		print("Unable to fetch "+book['dp']+" data from ZBOOK.");

	if hisl_price > float(book['price']):
		hisl_price = float(book['price']);
		hisl_date =  book['date'];
	
	sql2 = "UPDATE zbook SET book_name='%s', book_covr='%s', author='%s', oprice=%s, curr_price=%s, curr_date='%s', hisl_price=%s, hisl_date='%s', score=%.1f WHERE book_kid='%s' "%(\
		book['title'], book['image'], book['author'], book['oprice'], book['price'], book['date'], hisl_price, hisl_date, book['score'], book['dp']);
	print(sql2);
	try:
		#print(hisl_date+" : "+str(hisl_price));
		cs.execute(sql2);
		db.commit();
	except Exception as e:
		print(e);
		print("Unable to update "+book['dp']+" date into ZBOOK.");
	print("UPDATE SUCCESSFULLY.");

def sel_daily(db):
	books = [];
	cs = db.cursor();
	today = time.strftime("%Y-%m-%d", time.localtime());
	sql = "SELECT book_kid, book_name, book_covr, author, oprice, hisl_price, hisl_date, curr_price, score, FORMAT(curr_price/oprice*10,1) AS discount FROM zbook WHERE curr_date='%s'"%(today);
	print(sql);
	book = {};
	try:
		cs.execute(sql);
		results = cs.fetchall();
		for row in results:
			book = {};
			book['dp'] = row[0];
			book['title'] = row[1];
			book['image'] = row[2];
			book['author']= row[3];
			book['oprice']= row[4];
			book['lprice']= row[5];
			book['ldate'] = row[6];
			book['price'] = row[7];
			book['score'] = row[8];
			book['disct'] = row[9];
			books.append(book);
	except Exception as e:
		print(e);
		print("Could not select books from DB.");
	return books;

def reset_db(db):
	db.close();

def parse_amazon():
	l = parse_zbook();
	l = l+parse_weekly();
	print("There are ",len(l)," books to parse");
	books = [];
	for x in l:
		books.append(parse_one(x[0:14]));

	#parse_one("/dp/B076ZKV2MZ");	
	print(books);

	db = init_db();
	for book in books:
		tmp = check_book(book,db);
		if tmp == 0:
			insert_book(book, db);
		else:
			merge_book(book, db);

	reset_db();

if __name__ == '__main__':
	db = init_db();
	books = sel_daily(db);
	print(len(books));
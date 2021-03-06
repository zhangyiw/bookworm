from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from parse_zbook import *

app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/zbook')
def zbook(books=[]):
	db = init_db();
	if db:
		books = sel_daily(db);
		print("Select Out "+str(len(books))+" books.");
		return render_template('zbook.html',books=books);
	else:
		return render_template('404.html');

@app.route('/bfere')
def bfere():
    return render_template('bfere.html')

@app.route('/index')
def index1():
    with open('./templates/index1.html','r') as fd:
    	return fd.read();

if __name__ == '__main__':
    app.run(debug=True)

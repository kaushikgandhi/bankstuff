import subprocess
#Jai Manohar giri maharaj , Jai Gopal Giri Mahara

from flask import Flask
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,send_from_directory
import sys
import collections
reload(sys)
sys.setdefaultencoding('utf8')
import MySQLdb,json
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.contrib.atom import AtomFeed
import datetime
from random import randint

app = Flask(__name__, static_url_path='/static')
app.config.from_object(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# configuration
DATABASE = 'gopal_giri'
DB_SERVER = 'localhost'
DEBUG = True
SECRET_KEY = 'epicMedia123'
USERNAME = 'root'
PASSWORD = 'babamanohar'

#Mysql Connectio Declaration
class SQLconnection:
    def init(self):
        self.db = MySQLdb.connect(DB_SERVER,USERNAME,PASSWORD,DATABASE)
        self.db.autocommit(True)
        self.db.ping(True)
        self.cursor = self.db.cursor()
    def re_connect(self):
        self.db = MySQLdb.connect(DB_SERVER,USERNAME,PASSWORD,DATABASE)
        self.db.autocommit(True)
        self.db.ping(True)
        self.cursor = self.db.cursor()
    def close_connection(self):
        self.cursor.close()
        self.db.close()


def take_screenshot(url,_id):
	subprocess.call(["webkit2png","-o", "img/"+str(_id)+".png",url])

_connection = SQLconnection()
_connection.init()
_connection.cursor.execute('select namefull,id,website from bank_branches where BRNUM=0 group by namefull')

for bank in _connection.cursor.fetchall():
	print 'scrapping',bank
	take_screenshot(bank[2],bank[1])



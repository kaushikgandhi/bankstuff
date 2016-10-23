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
from flask import make_response
from flask import request

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
from flask import jsonify

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

import re

app.config.from_object(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

_connection = SQLconnection()
_connection.init()


@app.route('/robots.txt')
@app.route('/robots.txt/')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('fonts', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('/static/css', path)


@app.route('/')
def home():
  bank_names = {}
  try:
    _connection.cursor.execute('select namefull,id from bank_branches where BRNUM=0 and website!="To Be Updated" ORDER BY RAND() limit 20')
  except Exception as e:
    print e
    _connection.re_connect()
    return "There was an error reconnect in sometime"

  banks = [(_bank[1],_bank[0]) for _bank in _connection.cursor.fetchall()]

  return render_template('index.html',banks=banks)
@app.route('/search/<query>')
def search(query):
  bank_names = {}
  try:
    _connection.cursor.execute('select namefull,id from bank_branches where BRNUM=0 and website!="To Be Updated" and upper(namefull) like "%s" limit 20'%(query.upper()+'%'))
  except Exception as e:
    print e
    _connection.re_connect()
    return "There was an error reconnect in sometime"

  banks = [('/'+_bank[0].replace(' ','-')+"-online-banking-login/"+str(_bank[1])+'/',_bank[0]) for _bank in _connection.cursor.fetchall()]

  return jsonify(banks=banks)

@app.route('/<code>')
@app.route('/<code>/')
def with_letter(code):
  bank_names = {}
  try:
    _connection.cursor.execute('select namefull,id from bank_branches where BRNUM=0 and website!="To Be Updated" and namefull like "%s" group by namefull '%(code+'%'))
  except Exception as e:
    print e
    _connection.re_connect()
    return "There was an error reconnect in sometime"

  banks = [(_bank[1],_bank[0]) for _bank in _connection.cursor.fetchall()]
  for bank in banks:
    if bank:
      if bank[1][0].capitalize() not in bank_names.keys():
        bank_names[bank[1][0].capitalize()] = []
      bank_names[bank[1][0].capitalize()].append((bank[0],bank[1].strip()))
  print len(banks)
  bank_names = collections.OrderedDict(sorted(bank_names.items()))

  return render_template('with_code.html',banks_dict=bank_names,code=code)


def home_gen():
  return render_template('index_gn.html')

@app.route('/<bank_name>-online-banking-login/<code>')
@app.route('/<bank_name>-online-banking-login/<code>/')
def banklogin(bank_name,code):
  bank_names = {}
  try:
    _connection.cursor.execute('select ADDRESBR,id,CITYBR,STALPBR,ZIPBR,NAMEBR,NAMEFULL,Website,STNAMEBR,CNTYNAMB,SIMS_ESTABLISHED_DATE,NAMEHCR,city,stalp,brnum,\
                      UNINUMBR,BRSERTYP,DEPSUMBR,cert,INSAGNT1,INSURED,BKCLASS,BKMO,\
                       SIMS_ACQUIRED_DATE,HCTMULT,RSSDHCR,RSSDID,BKCLASS,FDICNAME,ASSET,OCCNAME from bank_branches where id=%d'%int(code))
    branch = _connection.cursor.fetchone()
    _connection.cursor.execute('select count(*) from bank_branches where namefull = "%s"'%branch[6])
    total_branches = _connection.cursor.fetchone()[0]
    branch={
          'address':branch[0],
          'id':branch[1],
          'city':branch[2],
          'state_code':branch[3],
          'zipcode':branch[4],
          'name':branch[5],
          'bank_name':branch[6],
          'web':branch[7],
          'state':branch[8],
          'county':branch[9],
          'est_date':branch[10],
          'hcr':branch[11]+', '+branch[12]+', '+branch[13],
          'brnum':branch[14],
          'UNINUMB':branch[15],
          'BRSERTYP':branch[16],
          'DEPSUMBR':branch[17],
          'FDICDBS':branch[18],
          'FDICNAME':branch[27],
          'INSAGNT1':branch[19],
          'INSURED':branch[20],
          'total_branches':total_branches,
          'BKCLASS':branch[21],
          'office_type':branch[22],
          'SIMS_ACQUIRED_DATE':branch[23],
          'HCTMULT':branch[24],
          'RSSDHCR':branch[25],
          'name_hcr':branch[11],
          'RSSDID':branch[12],
          'BKCLASS':branch[26],
          'FDIC_CITY':branch[28],
          'ASSET':branch[29],
          'OCCNAME':branch[30],

      }
  except Exception as e:
    print e
    _connection.re_connect()
    return "There was an error reconnect in sometime"

  return render_template('howtologin.html',bank=branch)

# a route for generating sitemap.xml
@app.route('/sitemap.<index>.xml', methods=['GET'])
def sitemap(index):
  """Generate sitemap.xml. Makes a list of urls and date modified."""
  pages=[]
  one_day_ago=(datetime.datetime.now() - datetime.timedelta(days=0)).date().isoformat()
  start = (int(index)-1) * 1000
  end = start + 1001
  if start>0:
    start=start+1
  bank_names = {}
  try:
    _connection.cursor.execute('select namefull,id from bank_branches where BRNUM=0 and website!="To Be Updated" group by NAMEFULL')
  except Exception as e:
    print e
    _connection.re_connect()
    return "There was an error reconnect in sometime"

  banks = [('/'+_bank[0].replace(' ','-')+"-online-banking-login/"+str(_bank[1])+'/',_bank[0]) for _bank in _connection.cursor.fetchall()]
  for bank in banks[start:end]:
    url = 'https://www.howtobanklogin.com'+bank[0]
    pages.append(
                  [url.replace('&',''),one_day_ago]
                )
  
  sitemap_xml = render_template('sitemap.xml', pages=pages)
  response= make_response(sitemap_xml)
  response.headers["Content-Type"] = "application/xml"    

  return response



if __name__ == '__main__':
    app.run(debug=True)

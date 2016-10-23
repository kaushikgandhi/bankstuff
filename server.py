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

import re

app.config.from_object(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

_connection = SQLconnection()
_connection.init()

@app.route('/robots.txt')
@app.route('/robots.txt/')
def robot():
    return render_template('robots.txt')

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

def get_type(url):
    url_split = url.split('-')
    if url == 'bank-locations' or  'bank-locations_' in url:
         return '','bank-locations',''
    elif 'bank-locations' in url:
        if 'state' in url_split[len(url_split)-1]:
            return 'STALPBR','bank-locations',url_split[2]
        if 'city' in url_split[len(url_split)-1]:
            return 'CITYBR','bank-locations',url_split[2]
        if 'county' in url_split[len(url_split)-1]:
            return 'CNTYNAMB','bank-locations',url_split[2]

    if url == 'all-banks' or  'all_banks_' in url:
         return 'namefull','all-banks',''
    elif 'all-banks' in url:
        if 'state' in url_split[len(url_split)-1]:
            return 'stnamebr','all-banks',url_split[2]
        if 'city' in url_split[len(url_split)-1]:
            return 'CITYBR','all-banks',url_split[2]
        if 'county' in url_split[len(url_split)-1]:
            return 'CNTYNAMB','all-banks',url_split[2]

    if url_split[len(url_split)-2] == 'branch_location_timings':
        return url_split[len(url_split)-1],'branch',''
    elif 'locations' in url_split[len(url_split)-1]:
        bank = ' '.join(st for st in url_split[:-1])
        print bank
        return bank,'branches',''
    elif 'state' in url_split[len(url_split)-1]:
        url_split = url.split('-In-')
        state = url_split[1].split('-')[0]
        bank = url_split[0].replace('-',' ')
        return bank,'branches_by_state',state
    elif 'city' in url_split[len(url_split)-1]:
        url_split = url.split('-In-')
        state = ' '.join(url_split[1].split('-')[0:-2])
        bank = url_split[0].replace('-',' ')
        return bank,'branches_by_city',state
    elif 'county' in url_split[len(url_split)-1]:
        url_split = url.split('-In-')
        state = ' '.join(url_split[1].split('-')[0:-2])
        bank = url_split[0].replace('-',' ')
        return bank,'branches_by_county',state


def get_branches(bank,url,type,param):
    bank_name = bank.replace('  ',' ').replace(' ','%')+'%'
    extra_query = ''
    if type and param:
        extra_query = 'and '+type+'="'+param+'"'
    _connection.cursor.execute('select ADDRESBR,id,CITYBR,STALPBR,ZIP,NAMEBR from bank_branches  where namefull like "%s"'%bank_name+extra_query)
    branches = [(branch[0],branch[1],branch[2],branch[3],branch[4],branch[5]) for branch in _connection.cursor.fetchall()]
    _connection.cursor.execute('select SIMS_ESTABLISHED_DATE,ASSET,NAMEHCR,CITY,STALP,count(*),INSAGNT1,Address,cert from bank_branches  where namefull like "%s"'%bank_name)
    hcr = [(branch[0],branch[1],branch[2],branch[3],branch[4],branch[5],branch[6],branch[7],branch[8]) for branch in _connection.cursor.fetchall()]
    print hcr
    head_branch = {
        "name":hcr[0][2],
        "location": hcr[0][7]+','+hcr[0][3]+','+hcr[0][4],
        "est_date":hcr[0][0],
        "assets":hcr[0][1],
        "total_branches":hcr[0][5],
        'INSAGNT1':hcr[0][6],
        'FDIC':hcr[0][8]
    }
    _connection.cursor.execute('select count(*) from bank_branches where namefull like "%s" '%bank_name+extra_query)
    total_pages = int(_connection.cursor.fetchone()[0]) / 25
    page = url.split('_')
    current_page = 0
    previous_page = None
    next_page = None
    if len(page)==2:
        current_page = int(page[1])
    if current_page > 0:
        previous_page = url.split('_')[0]+'_'+str(current_page-1)
    if current_page < total_pages:
        next_page = url.split('_')[0]+'_'+str(current_page+1)
    add_heading = ''
    from states import states
    if type == 'STALPBR':
        add_heading = states[param]+', '+param
    elif type == 'CITYBR':
        add_heading = param+', '+branches[0][3]
    elif type == 'CNTYNAMB':
        add_heading = param+', '+branches[0][3]

    _connection.cursor.execute('select distinct STNAMEBR,STALPBR,count(*)  from bank_branches  where namefull like "%s" GROUP by STNAMEBR'%bank_name)
    states = [(state[0],state[1],state[2]) for state in _connection.cursor.fetchall()]
    _connection.cursor.execute('select distinct CITYBR,STALPBR,COUNT(*) from bank_branches  where namefull like "%s" GROUP BY CITYBR ORDER BY RAND()'%bank_name)
    cities = [(city[0],city[1],city[2]) for city in _connection.cursor.fetchall()]
    _connection.cursor.execute('select distinct CNTYNAMB,STALPBR,COUNT(*)  from bank_branches  where namefull like "%s" GROUP BY CNTYNAMB ORDER BY RAND()'%bank_name)
    counties = [(county[0],county[1],county[2]) for county in _connection.cursor.fetchall()]
    return render_template('branches.html',count_cities = len(cities),count_states=len(states),add_heading=add_heading,head_branch=head_branch,bank=bank,branches=branches[current_page*25:(current_page*25+25)],previous=previous_page,next=next_page,total_pages=total_pages,current_page=current_page,counties=counties[0:50],states=states,cities=cities[0:50])

def get_all_locations(url,type,param):
    heading = 'All US Bank Locations'
    extra_query = ''
    if type and param:
        extra_query = ' where '+type+'="'+param+'"'


    _connection.cursor.execute('select ADDRESBR,id,CITYBR,STALPBR,ZIP,NAMEBR,namefull from bank_branches'+extra_query)

    branches = [(branch[0],branch[1],branch[2],branch[3],branch[4],branch[5],branch[6]) for branch in _connection.cursor.fetchall()]

    _connection.cursor.execute('select count(*) from bank_branches'+extra_query)
    total_pages = int(_connection.cursor.fetchone()[0]) / 25
    page = url.split('_')
    current_page = 0
    previous_page = None
    next_page = None
    if len(page)==2:
        current_page = int(page[1])
    if current_page > 0:
        previous_page = url.split('_')[0]+'_'+str(current_page-1)
    if current_page < total_pages:
        next_page = url.split('_')[0]+'_'+str(current_page+1)

    from states import states
    if type == 'STALPBR':
        heading = 'All Banks In '+states[param]+', '+param
    elif type == 'CITYBR':
        heading = 'All Banks In '+param+', '+branches[0][3]
    elif type == 'CNTYNAMB':
        heading = 'All Banks In '+param+', '+branches[0][3]

    _connection.cursor.execute('select distinct STNAMEBR,STALPBR,count(*)  from bank_branches GROUP by STNAMEBR')
    states = [(state[0],state[1],state[2]) for state in _connection.cursor.fetchall()]
    _connection.cursor.execute('select distinct CITYBR,STALPBR,COUNT(*) from bank_branches GROUP BY CITYBR ORDER BY RAND() limit 50')
    cities = [(city[0],city[1],city[2]) for city in _connection.cursor.fetchall()]
    _connection.cursor.execute('select distinct CNTYNAMB,STALPBR,COUNT(*)  from bank_branches GROUP BY CNTYNAMB ORDER BY RAND() limit 50')
    counties = [(county[0],county[1],county[2]) for county in _connection.cursor.fetchall()]
    return render_template('all-locations.html',heading=heading,branches=branches[current_page*25:(current_page*25+25)],previous=previous_page,next=next_page,total_pages=total_pages,current_page=current_page,counties=counties[0:50],states=states,cities=cities[0:50])

def get_all_banks(url,type,param):
        _connection.cursor.execute('select '+type+',count(*),stalpbr from bank_branches GROUP by '+type)
        bank_names = {}
        true_type = 'Bank'
        ledger = 'Browse By Bank Names'
        if type == 'stnamebr':
            true_type = 'state'
            ledger = 'Browse US Banks By States'
        elif type == 'CITYBR':
            true_type = 'city'
            ledger = 'Browse US Banks By Cities'
        elif type == 'CNTYNAMB':
            true_type = 'county'
            ledger = 'Browse US Banks By Counties'

        for bank in _connection.cursor.fetchall():
            bank_ = bank[0]
            if bank:
                if bank_[0].capitalize() not in bank_names.keys():
                    bank_names[bank_[0].capitalize()] = []
                    if type == 'namefull':
                        bank_names[bank_[0].capitalize()].append((bank[0],re.sub('[^A-Za-z0-9,.&\-\s]+', '', bank[0]).replace(' ','-')+'-locations',bank[1]))
                    elif true_type=='state':
                        bank_names[bank_[0].capitalize()].append((bank[0],'bank-locations-'+bank[2]+'-'+re.sub('[^A-Za-z0-9,.&\-\s]+', '', bank[0]).replace(' ','-')+'-state',bank[1]))
                    else:
                        bank_names[bank_[0].capitalize()].append((bank[0],'bank-locations-'+re.sub('[^A-Za-z0-9,.&\-\s]+', '', bank[0]).replace(' ','-')+'-'+bank[2]+'-'+true_type,bank[1]))
                else:
                    if type == 'namefull':
                        bank_names[bank_[0].capitalize()].append((bank[0],re.sub('[^A-Za-z0-9,.&\-\s]+', '', bank[0]).replace(' ','-')+'-locations',bank[1]))
                    elif true_type=='state':
                        bank_names[bank_[0].capitalize()].append((bank[0],'bank-locations-'+bank[2]+'-'+re.sub('[^A-Za-z0-9,.&\-\s]+', '', bank[0]).replace(' ','-')+'-state',bank[1]))
                    else:
                        bank_names[bank_[0].capitalize()].append((bank[0],'bank-locations-'+re.sub('[^A-Za-z0-9,.&\-\s]+', '', bank[0]).replace(' ','-')+'-'+bank[2]+'-'+true_type,bank[1]))


        import collections
        bank_names = collections.OrderedDict(sorted(bank_names.items()))
        return render_template('all-banks.html',true_type=true_type,banks_dict=bank_names,ledger=ledger)

def get_branch(id):
    _connection.cursor.execute('''select ADDRESBR,id,CITYBR,STALPBR,ZIPBR,NAMEBR,NAMEFULL,Website,
                      STNAMEBR,CNTYNAMB,SIMS_ESTABLISHED_DATE,NAMEHCR,city,stalp,brnum,
                      UNINUMBR,BRSERTYP,DEPSUMBR,cert,INSAGNT1,INSURED,BKCLASS,BKMO,
                       SIMS_ACQUIRED_DATE,HCTMULT,RSSDHCR,RSSDID,BKCLASS from bank_branches  where id= "%s"'''%id)
    branch = _connection.cursor.fetchone()
    _connection.cursor.execute('select count(*) from bank_branches where namefull = "%s"'%branch[6])
    total_branches = _connection.cursor.fetchone()[0]
    import datetime
    today = datetime.date.today()
    day = today.strftime('%A')
    now = datetime.datetime.now()
    hours = int(now.strftime('%H'))
    open = 'Closed Now'
    if day in ['Monday','Tuesday','Wednesday','Thrusday','Friday']:
        if hours > 8 and hours < 17:
            open = 'Open Now'
    return render_template('branch-page.html',branch={
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
        'BKCLASS':branch[26]

    },open=open,day=day)
    #return render_template('branches.html',bank=bank,branches=branches[current_page*50:(current_page*50+50)],previous=previous_page,next=next_page,total_pages=total_pages,current_page=current_page,counties=counties[0:50],states=states,cities=cities[0:50])

@app.route('/')
def home():
  bank_names = {}
  try:
    _connection.cursor.execute('select namefull,id from bank_branches where BRNUM=0 and website!="To Be Updated" group by namefull')
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

  return render_template('index.html',banks_dict=bank_names)


def home_gen():
  return render_template('index_gn.html')

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





if __name__ == '__main__':
    app.run(debug=True)

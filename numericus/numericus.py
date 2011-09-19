from bottle import route, run, validate, request
from datetime import datetime, timedelta
import belib.date.bedate as bedate
import belib.format.base23 as base23
import sqlite3

# Debug mode
from bottle import debug
debug(True)

# Create new DB
def createDB():
	conn = sqlite3.connect('used_no.sqlite3')
	c = conn.cursor()
	c.execute("CREATE TABLE revision (release_number INTEGER );")
	c.execute("INSERT INTO revision(release_number) values(1);")
	c.execute("CREATE TABLE object_numbers (no INTEGER, ip TEXT );")
	c.execute("CREATE TABLE sn_numbers (sn_no INTEGER, ip TEXT);")
	c.execute("CREATE TABLE boel_urls (be_url INTEGER, ip TEXT);")
	conn.commit()
	conn.close()


def calc(num=1, req_ip='not-supplied'):
	# Open sqlite DB and fetch last used number
	conn = sqlite3.connect('used_no.sqlite3')
	c = conn.cursor()
	
	c.execute("SELECT MAX(no) FROM object_numbers")
	row = c.fetchone()
	
	if row[0] is None:
		lastno = 0
	else:
		lastno = row[0]
	
	now = bedate.getBeStamp(datetime.now())
	# Check if current number is higher as lastno
	if now > lastno:
		calcdate = now+num-1
	else:
		calcdate = lastno+num

	# save starttime to db for security incl IP Adress of requester,
	## this way no duplicate number should occour.
	c.execute("INSERT INTO object_numbers(no,ip) VALUES (?,?)", (calcdate,req_ip))
	conn.commit()
	conn.close()

	res = {}			# container for result
	while num >= 1:
		conv = bedate.getBeStampEnc(calcdate)
		res[num] = conv['beWeek'] + '-' + conv['beSeconds']
		num = num-1
		calcdate = calcdate - 1
	return res

def calc_sn(num=1, req_ip='not-supplied'):
        # Open sqlite DB and fetch last used number
        conn = sqlite3.connect('used_no.sqlite3')
        c = conn.cursor()

        c.execute("SELECT MAX(sn_no) FROM sn_numbers")
        row = c.fetchone()

        if row[0] is None:
                lastno = 555
        else:
                lastno = row[0] + 1

	# Container for result
	res = {}
	res['quantity'] = num
	res['first'] = lastno

	# Calculate last number
        lastno = lastno+num-1

	#Store it
	res['last'] = lastno

        # save last sn number to db for security incl IP Adress of requester,
        ## this way no duplicate number should occour.
        c.execute("INSERT INTO sn_numbers(sn_no,ip) VALUES (?,?)", (lastno,req_ip))
        conn.commit()
        conn.close()

        return res

def calc_url(num=1, req_ip='not-supplied'):
        # Open sqlite DB and fetch last used number
        conn = sqlite3.connect('used_no.sqlite3')
        c = conn.cursor()

        c.execute("SELECT MAX(be_url) FROM boel_urls")
        row = c.fetchone()

        if row[0] is None:
                lastno = 0
        else:
                lastno = row[0] + 1

	# save last number to db before calculation for security incl IP Adress
	## of requester, this way no duplicate number should occour.
	c.execute("INSERT INTO boel_urls(be_url,ip) VALUES (?,?)", (lastno+num-1,req_ip))
	conn.commit()
	conn.close()
	
	res = {}	# container for result
	while num >= 1:
		url = base23.encode(lastno)
		res[num] = 'http://boel.ch/ln/' + url
		num = num-1
		lastno = lastno+1

	return res

def reset_db(req_ip='not-supplied'):
	conn = sqlite3.connect('used_no.sqlite3')
        c = conn.cursor()
        if req_ip == '192.168.1.48':
		c.execute("DROP TABLE boel_urls;")
		c.execute("CREATE TABLE boel_urls (be_url INTEGER, ip TEXT);")
		conn.commit()
		res = 'DB reseted'
	else:
		res = 'DB reset not allowed from this IP'

	conn.close()
	return res

@route('/numericus')
def returnOne():
	ip = request.environ.get('REMOTE_ADDR')
	res = calc(1,ip)
	return {'ObjNo': res}

@route('/numericus/:no#[0-9]+#')
@validate(no=int)
def returnMany(no):
	if no <= 23:
		ip = request.environ.get('REMOTE_ADDR')
		res = calc(no,ip)
		return {'ObjNo': res}

@route('/numericus/sn')
def returnOne():
        ip = request.environ.get('REMOTE_ADDR')
        res = calc_sn(1,ip)
        return {'SerialNo': res}

@route('/numericus/sn/:no#[0-9]+#')
@validate(no=int)
def returnMany(no):
        if no <= 100000000:
                ip = request.environ.get('REMOTE_ADDR')
                res = calc_sn(no,ip)
                return {'SerialNo': res}

@route('/numericus/url')
def returnOne():
        ip = request.environ.get('REMOTE_ADDR')
        res = calc_url(1,ip)
        return {'boelURL': res}

@route('/numericus/url/:no#[0-9]+#')
@validate(no=int)
def returnMany(no):
        if no <= 100000000:
                ip = request.environ.get('REMOTE_ADDR')
                res = calc_url(no,ip)
                return {'boelURL': res}

@route('/numericus/reset')
def returnOne():
        ip = request.environ.get('REMOTE_ADDR')
        res = reset_db(ip)
        return {'reset': res}

run(host='192.168.1.48',port=8000)


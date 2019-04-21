from flask import Flask
from flask import render_template,redirect,url_for,session,request
import serial
import time
import struct,sys
from connection import connection_database
import random
from datetime import datetime
from functools import wraps
import requests
import json

conn,cur = connection_database()


app = Flask(__name__)
app.secret_key='fkbkfdhdljdbdhdohdbkdh;dj;ndld'


finger_error = ''


@app.route('/')
def home():
	session.clear()
	return render_template("home.html")

@app.route('/redirect')
def redirect_page():
	session.clear()
	return render_template('redirect.html')

def login_required(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'ids' in session:
			return f(*args,**kwargs)
		else:
			return redirect(url_for('home'))
	return wrap

#background process happening without any refreshing
@app.route('/scan_finger')
def scan_finger():
	global finger_error 
	finger_error = ''
	ser = serial.Serial('COM7',57600)
	pack = [0xef01, 0xffffffff, 0x1]
	def printx():
	    for i in l:
	        print(i)
	    print( '')

	def readPacket():
	    time.sleep(1)
	    w = ser.inWaiting()
	    ret = []
	    if w >= 9:
	        s = ser.read(9) #partial read to get length
	        ret.extend(struct.unpack('!HIBH', s))
	        ln = ret[-1]

	        time.sleep(1)
	        w = ser.inWaiting()
	        if w >= ln:
	            s = ser.read(ln)
	            form = '!' + 'B' * (ln - 2) + 'H'
	            ret.extend(struct.unpack(form, s))
	    return ret


	def writePacket(data):
	    pack2 = pack + [(len(data) + 2)]
	    a = sum(pack2[-2:] + data)
	    pack_str = '!HIBH' + 'B' * len(data) + 'H'
	    l = pack2 + data + [a]
	    s = struct.pack(pack_str, *l)
	    ser.write(s)


	def verifyFinger():
	    data = [0x13, 0x0, 0, 0, 0]
	    writePacket(data)
	    s = readPacket()
	    return s[4]

	def genImg():
	    data = [0x1]
	    writePacket(data)
	    s = readPacket()
	    return s[4] 

	def img2Tz(buf):
	    data = [0x2, buf]
	    writePacket(data)
	    s = readPacket()
	    return s[4]

	def regModel():
	    data = [0x5]
	    writePacket(data)
	    s = readPacket()
	    return s[4]

	def search():
	    data = [0x4, 0x1, 0x0, 0x0, 0x0, 0x5]
	    writePacket(data)
	    s = readPacket()
	    return s[4:-1]  

	def mainfuncn():
	    if verifyFinger():
	        print( 'Verification Error')
	        sys.exit(-1)

	    print('Put finger')
	    sys.stdout.flush()

	    time.sleep(1)   
	    for _ in range(5):
	        g = genImg()
	        if g == 0:
	            break
	        time.sleep(1)

	        print( '.')
	        sys.stdout.flush()

	    print('')
	    sys.stdout.flush()
	    if g != 0:
	        sys.exit(-1)

	    if img2Tz(1):
	        print('Conversion Error')
	        sys.exit(-1)

	    r = search()
	    if r[0]==0:
	        print('Search result', r)
	        ids = str(r[2])
	        session['ids'] = ids
	        print("su")
	    else:
	    	global finger_error
	    	finger_error = "finger print is not registered!!"
	    	print("finger_error",finger_error)

	mainfuncn()
	print("finger_error",finger_error)
	if finger_error=='':
		data = [0,1,2,3,4,5,6,7,8,9]
		otp = ''
		for i in range(6):
			otp+=str(random.choice(data))
		session['otp'] = otp
		print(otp)
		query = "select * from fingertb where id = %s"
		cur.execute(query,(session['ids'],))
		res = cur.fetchone()
		URL = 'http://www.way2sms.com/api/v1/sendCampaign'
		session['mobile'] = res[2]
		session['balance']  = res[4]
		# get request
		def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
			req_params = {
			'apikey':apiKey,
  			'secret':secretKey,
  			'usetype':useType,
  			'phone': phoneNo,
  			'message':textMessage,
  			'senderid':senderId
  			}
			return requests.post(reqUrl, req_params)

			# get response
		response = sendPostRequest(URL, 'F6XIQDHSXOVGNVYF54BIHTZ8H6KK0EZ9', 'LTH85DZI8XGSGUY5', 'stage', session['mobile'], 'WAYSMS', 'your otp of atm access is '+otp)
		print response.text
		return redirect(url_for('verify'))
	else:
		return render_template("scanning1.html")
	return render_template('home.html')


@app.route('/verify',methods=["GET","POST"])
def verify():
	if request.method=="POST":
		data = request.form['otp_num']
		print(data)
		print(session)
		if session['otp'] == data:
			return redirect(url_for('sucess'))
		else:
			error = "otp invalid"
			return render_template("scanning1.html",error=error)

	return render_template("scanning.html",mobile=session['mobile'])

@app.route('/sucess')
@login_required
def sucess():
	return render_template("sucess.html")


@app.route('/withdraw',methods=["GET","POST"])
@login_required
def withdraw():
	error = ''
	if request.method=="POST":
		amount = request.form['amount']
		real_amount = int(session['balance'])-int(amount)
		if real_amount<0:
			error = "Insufficient balance!!!"
			return render_template("withdraw.html",error=error)
		query = "update fingertb set balance = %s where id = %s"
		cur.execute(query,(real_amount,session['ids']))
		conn.commit()
		now = datetime.now()
		date = now.strftime("%m/%d/%Y  %H:%M:%S")
		query = "insert into transaction(id,balance,balance_withdraw,withdraw_data)values(%s,%s,%s,%s)"
		cur.execute(query,(session['ids'],real_amount,amount,date))
		conn.commit()
		URL = 'http://www.way2sms.com/api/v1/sendCampaign'
		# get request
		def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
			req_params = {
			'apikey':apiKey,
  			'secret':secretKey,
  			'usetype':useType,
  			'phone': phoneNo,
  			'message':textMessage,
  			'senderid':senderId
  			}
			return requests.post(reqUrl, req_params)

		# get response
		message = "your account has been debiated with amount "+amount + " on " +date + " availabel balance in your account is "+str(real_amount)
		response = sendPostRequest(URL, 'F6XIQDHSXOVGNVYF54BIHTZ8H6KK0EZ9', 'LTH85DZI8XGSGUY5', 'stage', session['mobile'], 'WAYSMS', message)
		print response.text
		message = "your account has been debiated with amount "+amount + " on " +date + " availabel balance in your account is "+str(real_amount)
		print(message)
		return render_template("view_balance.html",balance=real_amount)
	return render_template('withdraw.html',error=error)

@app.route('/view_balance')
@login_required
def view_balance():
	return render_template('view_balance.html',balance=session['balance'])
	#return render_template('view_balance.html')

@app.route('/statement')
@login_required
def statement():
	query = "select * from transaction where id = %s"
	cur.execute(query,(session['ids'],))
	result = cur.fetchall()
	return render_template('statement.html',result=result)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
	app.run(debug=True)
# Import Useful libraries
import flask_login
import sms as sms
from flask_mysqldb import MySQL
import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, app
import re, requests
import MySQLdb.cursors
from database import Database
from user import User
import json
import datetime
from datetime import timedelta
import ast
from flask_wtf.csrf import CSRFProtect, CSRFError
import time
import random
import smtplib, ssl
from email.message import EmailMessage
from argon2 import PasswordHasher

# global Vars
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
#database = Database()
app.secret_key = "ming"
#app.config['SECRET_KEY'] = "ming"
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pa$$w0rd'
app.config['MYSQL_DB'] = 'pythonlogin'
mysql = MySQL(app)

def is_Human(captcha_response):
    cap_secret = "6Lc9JPYgAAAAAKwXOSxVBPMlh1FSq3HvMrE0K-gt"
    cap_data = {"response":captcha_response,"secret":cap_secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", cap_data)
    response_text = json.loads(response.text)
    return response_text['success']

#@app.route('/')
@app.route("/index")
def index():
    print('hi')
    if 'loggedin' in session:
        print("hi")
        return render_template("index.html")
    return redirect(url_for('login'))

#NEED REEEEEEEEEEEEEEE
@app.route("/display", methods=['post','get'])
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #account = database.getUserbyName(session['username'])
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        country = request.form['country']
        gender = request.form['gender']
        cursor = cursor.execute('select * from accounts where username = %s and password = %s and email = %s and country = %s and gender = %s', (username, password, email, country, gender))
        mysql.connection.commit()
        return render_template("display.html", cursor=cursor)
    return redirect(url_for('login'))

# Starting page which will be displayed to user when app is started
@app.route('/', methods=['GET', 'POST'])
def login():
    ph = PasswordHasher()
    # Message to be displayed
    msg = ''
    sitekey = "6Lc9JPYgAAAAAMxcrs-LwhfRXbK-yKNhh8ae-VTu"
    # Check is the call is post and fields are not empty
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        #account = database.getUser(username, password)
        captcha_response = request.form["g-recaptcha-response"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()


        # start session  If account exist otherwise display the message
        try:
            if ph.verify(account['password'], password):
                if is_Human(captcha_response):
                    session['loggedin'] = True
                    session['username'] = account['username']
                    msg = 'Logged in successfully !'
                    return render_template('index.html', msg=msg)

                if not is_Human(captcha_response):
                    session['loggedin'] = True
                    session['username'] = account['username']
                    msg = 'Please do the Captcha!'
                    return render_template('login.html', msg=msg, siteky=sitekey)
        except:
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            # Fetch one record and return result
            account = cursor.fetchone()
            flash("Please do the CAPTCHA")
            print(account['logincount'])
            newaccountlogincount=account['logincount']+1
            cursor.execute('UPDATE accounts set logincount = %s where id = %s;', (newaccountlogincount,account['id']))
            #cursor.execute(account['logincount']=newaccountlogincount)
            mysql.connection.commit()
            print(newaccountlogincount)
            if newaccountlogincount == 3:
                print("YEY")
                time.sleep(10)
                msg = 'timeout 30 secs'
                cursor.execute('UPDATE accounts set logincount = %s where id = %s;', (0,account['id']))
                mysql.connection.commit()
            msg = 'Incorrect username or Password'

    return render_template('login.html', msg=msg, siteky=sitekey)

# Function to signout the user when clicked
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Function to use for Registring the element
@app.route('/register', methods=['GET', 'POST'])
def register():
    ph = PasswordHasher()
    handStor=[]
    logincount='0'
    msg = ''
    # Check if the call is post and fields are not empty
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'country' in request.form and 'gender' in request.form:
        username = request.form['username']
        password = ph.hash(request.form['password'])
        email = request.form['email']
        phoneNO = request.form['phoneNO']
        country = request.form['country']
        gender = request.form['gender']
        print("hi")

        # Check if user with that username already exist
        #account = database.getUser(username, password)
        #if account:
        ###user = authy_api.users.create(email=email, phone=phoneNO, country_code=countrycode)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        account = cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        if cursor.execute('select * from accounts where username = %s and password = %s', (username, password,)):
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            #database.AddUser(User(username, password, gender, email, country))
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            print(handStor)
            #authyid = user.id
            authyid=0
            cursor.execute("insert into `accounts` (`id`, `username`, `password`, `email`, `country`, `gender`, `phoneNO`, `logincount`) values (NULL, %s, %s, %s, %s, %s, %s, %s);" , (username, password, email, country, gender, phoneNO, logincount))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            #msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

@app.route('/forgetpass', methods=['POST'])
def forgetpass():
    msg = ''
    ph=PasswordHasher()
    if 'loggedin' in session:
        if request.method == 'POST' and 'password' in request.form:
            password = ph.hash(request.form['password'])
            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Update accounts set password = %s where username = %s",(password,username))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
            return render_template("login.html")
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("forgetpass.html", msg=msg)
    return redirect(url_for('otpP1'))

@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    ph=PasswordHasher()
    if 'loggedin' in session:
        if request.method == 'POST' and 'password' in request.form:
            password = ph.hash(request.form['password'])
            username = session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Update accounts set password = %s where username = %s",(password,username))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
            return render_template("login.html")
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/otpP1", methods=[ 'GET','POST'])
def otpP1():
    msg = ''
    ph=PasswordHasher()
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = "%s"', (username))
        account = cursor.fetchone()


        # start session  If account exist otherwise display the message

        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            return render_template('otpP2.html', msg=msg)

    return render_template("otpP1.html", msg=msg)

@app.route('/otpP2', methods=['GET','POST'])
def otpP2():
    if 'loggedin' in session:
        otpno = random.randint(1000,9999)
        #email
        email_sender = 'beeeiruuui@gmail.com'
        email_password = 'waqmjwtqhowxsjty'
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from accounts where username ='%s'" % session['username'])

        cf = cursor.fetchone()

        email_receiver = '%s', cf['email']
        print(email_receiver)
        #print(cursor.execute("select `email` from `accounts` where `username` = '%s'; " % username))
        subject = 'OTP Number'
        body = """
        Your OTP Number is: %s
        If this Email was not meant for you, Please Ignore This Email
        """ % otpno
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        if request.method == 'POST' and 'otp' in request.form:
            otp = request.form['otp']
            if otp == otpno:
                return render_template('forgetpass.html')
            else:
                return render_template('otpP2.html')
        return render_template('otpP2.html')
    return redirect(url_for('otpP1'))

if __name__ == '__main__':
    app.run()
    #database.CloseDatabase(debug=True)

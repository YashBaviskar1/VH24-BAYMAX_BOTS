from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_mail import Mail, Message
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import random 
import pymysql, hashlib
from datetime import datetime
import os 
from user_agents import parse
from time import time 
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

# Flask-Mail for email-based OTP 

# using random to generate 6 digits random code 
# App password : pbwt yobq yuha aqbd
#gmail : baymaxbots@gmail.com
#Random OTP generation 
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    database='auth_service'
)
cursor = connection.cursor()


app = Flask(__name__)
mail= Mail(app)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='663123264011-0v8pcfogbmbbj700g6gmv09hdc74nsee.apps.googleusercontent.com',
    client_secret= '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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    redirect_uri='http://127.0.0.1:5000/oauth2callback',  
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'baymaxbots@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbwt yobq yuha aqbd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = 'key'
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
MAX_ATTEMPTS = 5
BLOCK_TIME =  timedelta(minutes=15)
user_attemps = 0
# def login_attempts(user):
#     failed_login = 0
#     if failed_login >= MAX_ATTEMPTS:
#         return False
#     else : 
#         return True
mail = Mail(app)
def generate_random_otp():
    otp_sent_to_mail = random.randint(100000, 999999)
    print(otp_sent_to_mail)
    return otp_sent_to_mail

def log_request():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    request_method = request.method
    request_url = request.url
    request_path = request.path
    user_agent_str = request.headers.get('User-Agent')
    
    user_agent = parse(user_agent_str)
    browser_name = user_agent.browser.family 
    browser_version = user_agent.browser.version_string
    os_name = user_agent.os.family  
    os_version = user_agent.os.version_string
    timestamp = datetime.now().isoformat()

    log_entry = LogEntry(
        timestamp=timestamp,
        client_ip=client_ip,
        request_method=request_method,
        request_url=request_url,
        request_path=request_path,
        user_agent=user_agent_str,
        browser_name=browser_name,
        browser_version=browser_version,
        os_name=os_name,
        os_version=os_version
    )
    print(f"Timestamp: {timestamp}")
    print(f"IP Address: {client_ip}")
    print(f"Request Method: {request_method}")
    print(f"Request URL: {request_url}")
    print(f"Request Path: {request_path}")
    print(f"User Agent: {user_agent_str}")
    print(f"Browser: {browser_name} {browser_version}")
    print(f"Operating System: {os_name} {os_version}")
    try:
        db.session.add(log_entry)
        db.session.commit()
        print("Log entry added successfully.")
    except Exception as e:
        print(f"Error adding log entry: {e}")

otp = generate_random_otp()
class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100))
    client_ip = db.Column(db.String(100))
    request_method = db.Column(db.String(10))
    request_url = db.Column(db.String(200))
    request_path = db.Column(db.String(200))
    user_agent = db.Column(db.String(200))
    browser_name = db.Column(db.String(100))
    browser_version = db.Column(db.String(100))
    os_name = db.Column(db.String(100))
    os_version = db.Column(db.String(100))
    def __repr__(self):
        return f'<Log {self.id}>'
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        salt = os.urandom(16).hex()  
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest() 
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("User already exists!", "error")
            return redirect(url_for('registration'))
        
        
        connection.commit()
        print(username, email, password)
        
        message_body = f"Your OTP to register is {otp}."
        msg = Message(subject='Your OTP for Registration', 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email])  
        msg.body = message_body
        mail.send(msg)
        cursor.execute("INSERT INTO users (username, password_hash, email, salt) VALUES (%s, %s, %s, %s)", (username, password_hash, email, salt))
        connection.commit()
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        request_method = request.method
        request_url = request.url
        request_path = request.path
        user_agent = request.user_agent.string
        timestamp = datetime.now().isoformat()

        print(client_ip)
        print(f"Timestamp: {timestamp}")
        print(f"IP Address: {client_ip}")
        print(f"Request Method: {request_method}")
        print(f"Request URL: {request_url}")
        print(f"Request Path: {request_path}")
        print(f"User Agent: {user_agent}")

        return redirect(url_for('authenticate'))


    return render_template("reg.html")

@app.route('/authenticate', methods = ['POST', 'GET'])
def authenticate():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp != str(otp) :
            return "InValid OTP Please try again"
        else :
            return redirect(url_for('login'))
    return render_template('authenticate.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/oauth2callback')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token() 
    user_info = google.get('userinfo').json()  
    session['profile'] = user_info  
    return f'Hello, {user_info["name"]}! You are signed in with Google.'

@app.route('/frontpage')
def frontpage():
    return render_template("frontpage.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            print("Fetched User Data:", user)

            if user:
                stored_password_hash = user[2]  
                stored_salt = user[3] 
                print("Stored Salt:", stored_salt)
                print("Stored Password Hash:", stored_password_hash)
                entered_password_hash = hashlib.sha256((stored_salt + password).encode()).hexdigest()

                print("Entered Password Hash:", entered_password_hash)


                if entered_password_hash == stored_password_hash:

                    # print("Login Successful")
                    session['username'] = username 
                    return redirect(url_for('frontpage'))
                else:
                    user_attemps = user_attemps + 1
                    print(f"User attempts : {user_attemps}")
                    flash("Wrong Password!", "error")
                    if user_attemps >= MAX_ATTEMPTS:

                        return redirect(url_for('blockpage'))

                    return redirect(url_for('login'))

            else:
                flash("Username does not exist!", "error")
#                 MAX_ATTEMPTS = 5
# BLOCK_TIME =  timedelta(minutes=15)
# user_attempt = 0
                user_attemps = user_attemps + 1
                print(f"User attempts : {user_attemps}")
                if user_attemps >= MAX_ATTEMPTS:
                    return redirect(url_for('blockpage'))
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)  
    elapsed_time = request.args.get('elapsedTime', '0m 0s') 
    log_request()
    print(elapsed_time)
    return redirect(url_for('metrics', elapsedTime=elapsed_time))

@app.route('/metrics')
def metrics():
    elapsed_time = request.args.get('elapsedTime', '0m 0s') 
    print(elapsed_time)
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    request_method = request.method
    request_url = request.url
    request_path = request.path
    user_agent_str = request.headers.get('User-Agent')
    timestamp = time()
    user_agent = parse(user_agent_str)
    browser_name = user_agent.browser.family 
    browser_version = user_agent.browser.version_string
    os_name = user_agent.os.family  
    os_version = user_agent.os.version_string
    
    timestamp = datetime.now().isoformat()
    return render_template('metrics.html', 
                           elapsed_time=elapsed_time, 
                           timestamp=timestamp,
                           client_ip=client_ip, 
                           request_method=request_method,
                           request_url=request_url,
                           request_path=request_path,
                           user_agent=user_agent_str,
                           browser=f"{browser_name} {browser_version}",
                           os=f"{os_name} {os_version}")

@app.route('/blockpage')
def blockpage():
    return render_template("blockpage.html")

if __name__ == '__main__':
    app.run(debug=True)
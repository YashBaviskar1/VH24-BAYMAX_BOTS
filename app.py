from flask import Flask, render_template, request, url_for, redirect
from flask_mail import Mail, Message
import random 
import pymysql, hashlib
from datetime import datetime
import os 
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

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'baymaxbots@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbwt yobq yuha aqbd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
def generate_random_otp():
    otp_sent_to_mail = random.randint(100000, 999999)
    print(otp_sent_to_mail)
    return otp_sent_to_mail

def log_request():
    # Capture various information from the request
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    request_method = request.method
    request_url = request.url
    request_path = request.path
    user_agent = request.user_agent.string
    timestamp = datetime.now().isoformat()

    # Print the captured information
    print(f"Timestamp: {timestamp}")
    print(f"IP Address: {client_ip}")
    print(f"Request Method: {request_method}")
    print(f"Request URL: {request_url}")
    print(f"Request Path: {request_path}")
    print(f"User Agent: {user_agent}")
otp = generate_random_otp()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        salt = os.urandom(16).hex()  # Generate a random salt
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()  # Hash the password with salt
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return "User already exists!"
        
        
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

        # Print the captured information
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



@app.route('/frontpage')
def frontpage():
    return render_template("frontpage.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # Fetch user details from the database based on the provided username
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            # Print user details for debugging
            print("Fetched User Data:", user)

            if user:
                stored_password_hash = user[2]  
                stored_salt = user[3] 
                print("Stored Salt:", stored_salt)
                print("Stored Password Hash:", stored_password_hash)
                entered_password_hash = hashlib.sha256((stored_salt + password).encode()).hexdigest()

                print("Entered Password Hash:", entered_password_hash)


                if entered_password_hash == stored_password_hash:
                    print("Login Successful")
                    return redirect(url_for('frontpage'))
                else:
                    print("Wrong Password")
                    return "Wrong Password!"
            else:
                print("Username does not exist")
                return "Username does not exist!"

        except Exception as e:
            print("Error during login:", str(e))
            return f"An error occurred: {str(e)}"
    
    return render_template("login.html")




if __name__ == '__main__':
    app.run(debug=True)
<<<<<<< HEAD
from flask import Flask, render_template, request
from flask_mail import Mail, Message
import random 

# Flask-Mail for email-based OTP 

# using random to generate 6 digits random code 
# App password : pbwt yobq yuha aqbd
#gmail : baymaxbots@gmail.com
#Random OTP generation 

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

generate_random_otp()


@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print(username, email, password)
        otp = generate_random_otp()
        otp = generate_random_otp()
        message_body = f"Your OTP to register is {otp}."
        msg = Message(subject='Your OTP for Registration', 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email])  # Send the OTP to the user's email
        msg.body = message_body
        mail.send(msg)
        return"Email sent successfuly"


    return render_template("reg.html")

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Mock database (use a real database in production)
users = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "User already exists!"
        users[username] = password
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('home'))
        return "Invalid credentials!"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 270a8b403e14367e42e679f81b319b24ff36ccec

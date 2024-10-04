from flask import Flask, render_template, request, url_for, redirect
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


#otp = generate_random_otp()
otp = 123456
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print(username, email, password)
        
        message_body = f"Your OTP to register is {otp}."
        msg = Message(subject='Your OTP for Registration', 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email])  
        msg.body = message_body
        #mail.send(msg)
        return redirect(url_for('authenticate'))


    return render_template("reg.html")

@app.route('/authenticate', methods = ['POST', 'GET'])
def authenticate():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp != str(otp) :
            return "InValid OTP Please try again"
        else :
            return redirect(url_for('frontpage'))
    return render_template('authenticate.html')



@app.route('/frontpage')
def frontpage():
    return render_template("frontpage.html")




if __name__ == '__main__':
    app.run(debug=True)
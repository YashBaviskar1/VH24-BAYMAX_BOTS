import json
from flask import Flask, render_template, request, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['SESSION_COOKIE_NAME'] = 'my-session'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Load Google OAuth credentials from JSON file
with open('client_secret.json') as f:  # Make sure the filename matches your downloaded file
    google_config = json.load(f)
    client_id = google_config['web']['client_id']
    client_secret = google_config['web']['client_secret']

# Set up Google OAuth
google_bp = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    redirect_to='google_login',  # Endpoint to handle the callback
    scope=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]  # Necessary scopes for user info
)
app.register_blueprint(google_bp, url_prefix='/google')

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

@app.route('/google/login')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get("/oauth2/v3/userinfo")  # Changed endpoint to use /userinfo
    assert resp.ok, resp.text
    return f"You are logged in as: {resp.json()['name']}"  # Display user name

if __name__ == '__main__':
    app.run(debug=True)

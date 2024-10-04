from flask import Flask, render_template, request, redirect, url_for
import pymysql
import hashlib
import os

app = Flask(__name__)

# Database connection
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='29092004',
    database='auth_service'
)
cursor = connection.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        salt = os.urandom(16).hex()  # Generate a random salt
        password_hash = hashlib.sha256((salt + password).encode()).hexdigest()  # Hash the password with salt
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return "User already exists!"
        
        cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)", (username, password_hash, salt))
        connection.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            # Hash the entered password with the stored salt
            stored_salt = user[3]  # Assuming the salt is the fourth column
            password_hash = hashlib.sha256((stored_salt + password).encode()).hexdigest()
            
            if user[2] == password_hash:  # Check against stored password_hash
                return redirect(url_for('home'))
        return "Invalid credentials!"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
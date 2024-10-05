from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, session, jsonify 
from flask_mail import Mail, Message
from flask_session import Session
import random
import pymysql
import hashlib
from datetime import datetime
import os
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from user_agents import parse
from time import time
import pickle
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from tabulate import tabulate

app = Flask(__name__)
mail = Mail(app)


connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    database='auth_service'
)
cursor = connection.cursor()

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'baymaxbots@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbwt yobq yuha aqbd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = 'key'
app.config['SESSION_TYPE'] = 'filesystem'
db_path = r"C:\Users\YashB\OneDrive\Desktop\Baymax_Bots_VH\hackathon\VH24-BAYMAX_BOTS\instance\logs.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
mail = Mail(app)
df = pd.read_csv("cleaned_40k.csv")
class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    client_ip = db.Column(db.String(50), nullable=False)
    request_method = db.Column(db.String(10), nullable=False)
    request_url = db.Column(db.String(200), nullable=False)
    request_path = db.Column(db.String(200), nullable=False)
    user_agent = db.Column(db.String(200), nullable=False)
    browser_name = db.Column(db.String(50), nullable=False)
    browser_version = db.Column(db.String(20), nullable=False)
    os_name = db.Column(db.String(50), nullable=False)
    os_version = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<LogEntry {self.id}: {self.timestamp}, {self.client_ip}, {self.request_method}>'
@app.route('/')
def index():
    return render_template('dashboard.html')

# with open('model_pipeline_ls.pkl', 'rb') as f:
#     model = pickle.load(f)


@app.route('/graph/<graph_type>')
def get_graph(graph_type):
    if df is None:
        return jsonify({'error': 'No data uploaded. Please upload a CSV file first.'}), 400

    if graph_type == 'attack_os':
        return attack_ips_by_os()
    elif graph_type == 'attack_browser':
        return attack_ips_by_browser()
    elif graph_type == 'attack_country':
        return attack_ips_by_country()
    elif graph_type == 'login_correlation':
        return correlation_login_device_browser()
    elif graph_type == 'mobile_login_success':
        return login_success_rate_mobile()
    else:
        return jsonify({'error': 'Invalid graph type'}), 400


@app.route('/logger')
def logger():
    return render_template("logger.html")

@app.route('/api/ip_logger', methods=['GET'])
def get_ip_logger_data():
    with app.app_context():
        log_entries = LogEntry.query.all()
        log_data = []
        for entry in log_entries:
            log_data.append({
                'timestamp': entry.timestamp,
                'ip_address': entry.client_ip,
                'user_agent': entry.user_agent,
                'request_method': entry.request_method,
                'request_url': entry.request_url
            })
        return jsonify(log_data)

def attack_ips_by_os():
    attack_ips = df[df['Is Attack IP'] == True]
    os_counts = attack_ips['OS Name and Version'].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    os_counts.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Operating Systems by Number of Attack IPs')
    plt.xlabel('Operating System')
    plt.ylabel('Number of Attack IPs')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return save_plot()

def attack_ips_by_browser():
    attack_ips = df[df['Is Attack IP'] == True]
    attack_ips['Browser Name'] = attack_ips['Browser Name and Version'].str.split(' ').str[0]
    browser_counts = attack_ips['Browser Name'].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    browser_counts.plot(kind='bar', color='salmon')
    plt.title('Top 10 Browsers by Number of Attack IPs')
    plt.xlabel('Browser Type')
    plt.ylabel('Number of Attack IPs')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return save_plot()

def attack_ips_by_country():
    attack_ips = df[df['Is Attack IP'] == True]
    country_counts = attack_ips['Country'].value_counts().head(10)

    plt.figure(figsize=(10, 6))
    country_counts.plot(kind='bar', color='lightblue')
    plt.title('Top 10 Countries by Number of Attack IPs')
    plt.xlabel('Country')
    plt.ylabel('Number of Attack IPs')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return save_plot()

def correlation_login_device_browser():
    df['Device Type'] = df['Device Type'].astype('category')
    df['Browser Name and Version'] = df['Browser Name and Version'].astype('category')
    correlation_matrix = df[['Login Successful', 'Device Type', 'Browser Name and Version']].apply(lambda x: x.cat.codes if x.dtype.name == 'category' else x).corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm')
    plt.title('Correlation between Login Success, Device Type, and Browser Type')
    plt.tight_layout()

    return save_plot()

def login_success_rate_mobile():
    mobile_success_counts = df[df['Device Type'] == 'mobile']['Login Successful'].value_counts()

    plt.figure(figsize=(8, 8))
    plt.pie(mobile_success_counts, labels=mobile_success_counts.index, autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#F44336'])
    plt.axis('equal')
    plt.title('Login Success Rate for Mobile Devices')
    plt.tight_layout()

    return save_plot()

def save_plot():
    # Save the plot to a BytesIO object and encode it to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf8')
    plt.close()  
    return jsonify({'data': [{'type': 'image', 'source': f'data:image/png;base64,{image_base64}'}], 'layout': {}})


if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from tabulate import tabulate

db_path = r"C:\Users\YashB\OneDrive\Desktop\Baymax_Bots_VH\hackathon\VH24-BAYMAX_BOTS\instance\logs.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

def fetch_log_entries():
    with app.app_context():
        log_entries = LogEntry.query.all()
        table_data = []
        for entry in log_entries:
            table_data.append([
                entry.id,
                entry.timestamp,
                entry.client_ip,
                entry.request_method,
                entry.request_url,
                entry.browser_name,
                entry.os_name
            ])
        
        headers = ['ID', 'Timestamp', 'IP Address', 'Request Method', 'Request URL', 'Browser', 'OS']
        
        print(tabulate(table_data, headers=headers, tablefmt='grid'))

if __name__ == '__main__':
    fetch_log_entries()

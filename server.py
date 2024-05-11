from flask import Flask, request
import psycopg2
import sys
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)



def create_table():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS uuids (username TEXT, uuid TEXT, status TEXT DEFAULT \'pending\')')
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)

@app.route('/')
def home():
    return "Home"

@app.route('/send_uuid', methods=['POST'])
def receive_uuid():
    try:
        uuid = request.form.get('uuid')
        username = request.form.get('username')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute('INSERT INTO uuids VALUES (%s, %s, %s)', (username, uuid, 'pending'))
        conn.commit()
        conn.close()
        return "Pending approval", 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return "Error occurred", 500

@app.route('/check_uuid', methods=['GET'])
def check_uuid():
    uuid = request.args.get('uuid')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute('SELECT * FROM uuids WHERE uuid=%s AND status=%s', (uuid, 'active'))
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        return "UUID exists", 200
    else:
        return "UUID does not exist or is not active", 404

@app.route('/api/check_uuid', methods=['GET'])
def api_check_uuid():
    uuid = request.args.get('uuid')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute('SELECT * FROM uuids WHERE uuid=%s AND status=%s', (uuid, 'active'))
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        return {"exists": True}, 200
    else:
        return {"exists": False}, 404

@app.route('/approve_user', methods=['POST'])
def approve_user():
    username = request.form.get('username')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute('UPDATE uuids SET status = %s WHERE username = %s', ('active', username))
    conn.commit()
    conn.close()
    return "User approved", 200

@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form.get('username')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute('DELETE FROM uuids WHERE username = %s', (username,))
    conn.commit()
    conn.close()
    return "User deleted", 200

# if __name__ == "__main__":
create_table()
app.run()

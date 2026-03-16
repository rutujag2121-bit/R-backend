from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import hashlib
import subprocess

app = Flask(__name__)
CORS(app)  # ZAP VULNERABILITY: Wildcard CORS - allows any origin (detected by ZAP)

# ----------------------------------------------------------------
# INTENTIONAL VULNERABILITY FOR SONARQUBE DETECTION
# Hardcoded secret key - SonarQube flags this as a critical security hotspot
# ----------------------------------------------------------------
app.config['SECRET_KEY'] = 'hardcoded-super-secret-key-12345'
DATABASE = 'users.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    # Insert a demo user
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, password, email) VALUES (1, 'admin', 'admin123', 'admin@example.com')"
    )
    conn.commit()
    conn.close()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Backend is running"})


# ----------------------------------------------------------------
# INTENTIONAL VULNERABILITY: SQL Injection (for SonarQube SAST detection)
# SonarQube detects unsanitised user input concatenated into SQL query
# ----------------------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    conn = get_db()
    cursor = conn.cursor()

    # SONARQUBE VULNERABILITY: SQL Injection - string formatting used in SQL query
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)  # noqa: S608
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "message": "Login successful", "user": user['username']})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')

    # INTENTIONAL VULNERABILITY: MD5 used for password hashing
    # SonarQube flags MD5 as a weak cryptographic algorithm
    hashed_password = hashlib.md5(password.encode()).hexdigest()  # noqa: S324

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        (username, hashed_password, email)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "User created"}), 201


# ----------------------------------------------------------------
# INTENTIONAL VULNERABILITY FOR ZAP DETECTION
# Reflected XSS: user input reflected back without sanitisation
# ZAP active scan detects this via reflected parameter in response
# ----------------------------------------------------------------
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # ZAP VULNERABILITY: Unsanitised user input reflected directly into response
    return jsonify({
        "query": query,  # Reflected XSS vector - ZAP injects script tags here
        "results": [],
        "message": f"Search results for: {query}"
    })


# ----------------------------------------------------------------
# INTENTIONAL VULNERABILITY: Command Injection (SonarQube detection)
# ----------------------------------------------------------------
@app.route('/api/ping', methods=['GET'])
def ping():
    host = request.args.get('host', 'localhost')
    # SONARQUBE VULNERABILITY: OS command injection via unsanitised input
    result = subprocess.run(  # noqa: S603, S607
        f"ping -c 1 {host}",
        shell=True,
        capture_output=True,
        text=True
    )
    return jsonify({"output": result.stdout})


if __name__ == '__main__':
    init_db()
    # ZAP VULNERABILITY: Debug mode enabled in production (information disclosure)
    app.run(host='0.0.0.0', port=5000, debug=True)

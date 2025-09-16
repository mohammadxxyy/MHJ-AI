import os
import sqlite3
import hashlib
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import openai
from dotenv import load_dotenv

# قم بتحميل متغيرات البيئة من ملف .env
load_dotenv()

# تهيئة تطبيق Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

# قم بتكوين OpenAI API
openai.api_key = os.environ.get("API_KEY")

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# عند بدء التطبيق لأول مرة
with app.app_context():
    init_db()

# مساعدة: توليد تجزئة لكلمة المرور (للاستخدام المحلي فقط)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# مسار الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# مسار صفحة تسجيل الدخول
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# مسار صفحة التسجيل
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# مسار أداة الذكاء الاصطناعي
@app.route('/ai_tool', methods=['GET'])
def ai_tool():
    if 'username' in session:
        return render_template('ai_tool.html')
    return redirect(url_for('login_page'))

# مسار تسجيل المستخدمين
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    hashed_password = hash_password(password)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return jsonify({"success": True, "message": "User registered successfully."}), 201
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists."}), 409
    finally:
        conn.close()

# مسار تسجيل الدخول
@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    hashed_password = hash_password(password)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return jsonify({"success": True, "message": "Login successful."}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

# مسار تسجيل الخروج
@app.route('/api/logout')
def logout_user():
    session.pop('username', None)
    return redirect(url_for('login_page'))

# مسار لتوليد رد من الذكاء الاصطناعي
@app.route('/api/generate', methods=['POST'])
def generate_response():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"success": False, "message": "Message is required."}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )
        return jsonify({"success": True, "response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# مسار معلومات الموقع
@app.route('/info')
def info_page():
    return render_template('info.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
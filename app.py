from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import hashlib
import openai
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# إعداد مفتاح API الخاص بـ OpenAI
openai.api_key = os.getenv('API_KEY')

# دالة لتهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات عند بدء التطبيق
init_db()

# مسار الصفحة الرئيسية
@app.route('/')
def home_page():
    return render_template('index.html')

# مسار صفحة تسجيل الدخول
@app.route('/login')
def login_page():
    return render_template('login.html')

# مسار صفحة إنشاء حساب
@app.route('/register')
def register_page():
    return render_template('register.html')

# مسار صفحة أداة الذكاء الاصطناعي
@app.route('/ai_tool')
def ai_tool_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('ai_tool.html')

# مسار واجهة برمجة تطبيقات تسجيل الدخول
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and hashlib.sha256(password.encode()).hexdigest() == user[1]:
        session['user_id'] = user[0]
        return jsonify({'message': 'تم تسجيل الدخول بنجاح!'}), 200
    else:
        return jsonify({'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'}), 401

# مسار واجهة برمجة تطبيقات إنشاء الحساب
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return jsonify({'message': 'تم إنشاء الحساب بنجاح!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'اسم المستخدم موجود بالفعل.'}), 409
    finally:
        conn.close()

# مسار واجهة برمجة تطبيقات توليد النص بالذكاء الاصطناعي
@app.route('/api/generate', methods=['POST'])
def api_generate():
    if 'user_id' not in session:
        return jsonify({'message': 'غير مصرح لك. يرجى تسجيل الدخول.'}), 401
    
    data = request.json
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'message': 'الرجاء تقديم مطالبة.'}), 400

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return jsonify({'response': response.choices[0].text.strip()}), 200
    except Exception as e:
        return jsonify({'message': f'حدث خطأ في طلب الذكاء الاصطناعي: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
from flask import Flask, render_template, request, jsonify
from flask_bcrypt import Bcrypt
import sqlite3
import google.generativeai as genai

# تم وضع مفتاح API الخاص بك هنا
API_KEY = "AIzaSyDFpoPomq_91JVtXWC-A8cKOwgipCs9vSo"
genai.configure(api_key=API_KEY)

app = Flask(__name__)
bcrypt = Bcrypt(app)

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# دالة لإنشاء جدول المستخدمين
def create_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# المسارات لعرض الصفحات
@app.route('/')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/ai_tool')
def ai_tool_page():
    return render_template('ai_chat.html')

@app.route('/info')
def info_page():
    return render_template('info.html')

# نقاط API لاستقبال البيانات
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "تم التسجيل بنجاح!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "اسم المستخدم أو البريد الإلكتروني موجود بالفعل."}), 409
    except Exception as e:
        return jsonify({"message": "حدث خطأ أثناء التسجيل."}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    if user and bcrypt.check_password_hash(user['password'], password):
        return jsonify({
            "message": "تم تسجيل الدخول بنجاح!",
            "username": user['username'],
            "email": user['email']
        }), 200
    else:
        return jsonify({"message": "البريد الإلكتروني أو كلمة المرور غير صحيحة."}), 401

# نقطة API جديدة للاتصال بالذكاء الاصطناعي
@app.route('/api/generate', methods=['POST'])
def generate_response():
    data = request.get_json()
    user_prompt = data.get('prompt')
    if not user_prompt:
        return jsonify({"error": "الطلب فارغ"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_prompt)
        return jsonify({"response": response.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)
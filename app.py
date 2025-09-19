from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import hashlib
import os
import uuid
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# إعداد عميل OpenAI
openai_client = OpenAI(api_key=os.getenv("API_KEY"))

# إعداد عميل Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

# دالة لتهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات عند بدء التطبيق
init_db()

# مسارات الصفحات الأساسية
@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/ai_tool')
def ai_tool_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('ai_tool.html')

# مسار جديد لصفحة الطلاب
@app.route('/students_tool')
def students_tool_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('students_tool.html')

# مسارات واجهات برمجة التطبيقات (API)
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, is_verified FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and hashlib.sha256(password.encode()).hexdigest() == user[1]:
        if user[2] == 1:
            session['user_id'] = user[0]
            return jsonify({'message': 'تم تسجيل الدخول بنجاح!'}), 200
        else:
            return jsonify({'message': 'حسابك غير مفعل. يرجى التحقق من بريدك الإلكتروني.'}), 401
    else:
        return jsonify({'message': 'اسم المستخدم أو كلمة المرور غير صحيحة.'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        verification_token = str(uuid.uuid4())
        cursor.execute('INSERT INTO users (username, email, password, is_verified, verification_token) VALUES (?, ?, ?, 0, ?)', (username, email, hashed_password, verification_token))
        conn.commit()
        return jsonify({'message': 'تم إنشاء الحساب بنجاح. يرجى تفعيله.'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'اسم المستخدم أو البريد الإلكتروني موجودان بالفعل.'}), 409
    finally:
        conn.close()

# مسار جديد لتفعيل الحساب (لأغراض الاختبار)
@app.route('/verify/<token>')
def verify_account(token):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_verified = 1, verification_token = NULL WHERE verification_token = ?', (token,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected > 0:
        return "تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول."
    else:
        return "رمز التفعيل غير صالح أو انتهت صلاحيته."

# مسار واجهة برمجة تطبيقات توليد النص بالذكاء الاصطناعي
@app.route('/api/generate', methods=['POST'])
def api_generate():
    if 'user_id' not in session:
        return jsonify({'message': 'غير مصرح لك. يرجى تسجيل الدخول.'}), 401
    
    data = request.json
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'message': 'الرجاء تقديم مطالبة.'}), 400

    # استخدام نموذج OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({'response': response.choices[0].message.content.strip()}), 200
    except Exception as e:
        return jsonify({'message': f'حدث خطأ في طلب الذكاء الاصطناعي: {str(e)}'}), 500

# مسار جديد لتلخيص الكتب
@app.route('/api/summarize_book', methods=['POST'])
def api_summarize_book():
    if 'user_id' not in session:
        return jsonify({'message': 'غير مصرح لك. يرجى تسجيل الدخول.'}), 401
    
    data = request.json
    book_text = data.get('book_text')

    if not book_text:
        return jsonify({'message': 'الرجاء تقديم نص الكتاب للتلخيص.'}), 400

    try:
        prompt = f"قم بتلخيص هذا الكتاب بشكل موجز: {book_text}"
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({'response': response.choices[0].message.content.strip()}), 200
    except Exception as e:
        return jsonify({'message': f'حدث خطأ في طلب الذكاء الاصطناعي: {str(e)}'}), 500

# مسار جديد لإنشاء اختبار
@app.route('/api/create_test', methods=['POST'])
def api_create_test():
    if 'user_id' not in session:
        return jsonify({'message': 'غير مصرح لك. يرجى تسجيل الدخول.'}), 401
    
    data = request.json
    content = data.get('content')

    if not content:
        return jsonify({'message': 'الرجاء تقديم محتوى لإنشاء الاختبار.'}), 400

    try:
        prompt = f"بناءً على المحتوى التالي، قم بإنشاء اختبار يتكون من 5 أسئلة اختيار من متعدد مع الإجابات الصحيحة: {content}"
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({'response': response.choices[0].message.content.strip()}), 200
    except Exception as e:
        return jsonify({'message': f'حدث خطأ في طلب الذكاء الاصطناعي: {str(e)}'}), 500

# مسار جديد يسمح بالاختيار بين النموذجين
@app.route('/api/generate_multi', methods=['POST'])
def api_generate_multi():
    if 'user_id' not in session:
        return jsonify({'message': 'غير مصرح لك. يرجى تسجيل الدخول.'}), 401
    
    data = request.json
    prompt = data.get('prompt')
    model_choice = data.get('model_choice', 'openai') # الافتراضي هو openai

    if not prompt:
        return jsonify({'message': 'الرجاء تقديم مطالبة.'}), 400

    try:
        if model_choice == 'openai':
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return jsonify({'response': response.choices[0].message.content.strip()}), 200
        elif model_choice == 'gemini':
            response = gemini_model.generate_content(prompt)
            return jsonify({'response': response.text}), 200
        else:
            return jsonify({'message': 'خيار النموذج غير صالح.'}), 400
    except Exception as e:
        return jsonify({'message': f'حدث خطأ في طلب الذكاء الاصطناعي: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

import os
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_ultra_secret')

# --- CONFIGURATION (Render Optimized) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Database-e Code ebong Desc column ensure kora
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, price TEXT, img TEXT, 
                     code TEXT, desc TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- CSS (Premium Mobile UI) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #fff; color: var(--primary); }
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.9); backdrop-filter: blur(10px); border-bottom: 1px solid #eee; z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; text-decoration: none; color: #000; letter-spacing: -1px; }
    .logo span { color: var(--accent); }
    .container { max-width: 600px; margin: auto; padding: 20px; }
    .btn { width: 100%; padding: 15px; border-radius: 12px; border: none; font-weight: bold; cursor: pointer; }
    .input { width: 100%; padding: 12px; margin-bottom: 12px; border-radius: 10px; border: 1px solid #ddd; font-family: inherit; }
</style>
'''

# --- ALL ROUTES ---

@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
        <body>
            <nav class="nav"><a href="/" class="logo">KHATA<span>KHORI</span></a></nav>
            <div style="padding: 20px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                {% for p in products %}
                <div style="border: 1px solid #eee; border-radius: 20px; overflow: hidden; background: #fff;">
                    <img src="{{ p['img'] }}" style="width: 100%; height: 180px; object-fit: cover;">
                    <div style="padding: 12px; text-align: center;">
                        <small style="color: #999; font-size: 10px;">{{ p['code'] }}</small>
                        <h4 style="margin: 5px 0; font-size: 14px;">{{ p['name'] }}</h4>
                        <p style="color: #e63946; font-weight: 800; margin: 0;">Tk {{ p['price'] }}</p>
                    </div>
                </div>
                {% else %}
                <p style="grid-column: span 2; text-align: center; color: #999; margin-top: 50px;">No products found. Go to /login to add.</p>
                {% endfor %}
            </div>
        </body></html>
    ''', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect(url_for('dashboard'))
    return render_template_string('''
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
        <body style="display:flex; align-items:center; justify-content:center; height:100vh; background:#f4f4f4;">
            <form method="POST" style="background:white; padding:30px; border-radius:20px; width:300px;">
                <h2 style="margin-top:0;">Admin Access</h2>
                <input name="u" class="input" placeholder="Username" required>
                <input name="p" type="password" class="input" placeholder="Password" required>
                <button class="btn" style="background:#000; color:#fff;">Login</button>
            </form>
        </body></html>
    ''')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
        <body style="background:#f8f9fa;">
            <nav class="nav"><span class="logo">DASH<span>BOARD</span></span><a href="/logout">Logout</a></nav>
            <div class="container">
                <form action="/add" method="POST" enctype="multipart/form-data" style="background:white; padding:20px; border-radius:20px;">
                    <input name="n" class="input" placeholder="Product Name" required>
                    <input name="c" class="input" placeholder="Product Code (e.g. KK-101)" required>
                    <input name="p" class="input" placeholder="Price" type="number" required>
                    <textarea name="d" class="input" style="height:80px;" placeholder="Description"></textarea>
                    <input type="file" name="file" class="input" accept="image/*" required>
                    <button class="btn" style="background:#000; color:#fff;">Publish Product</button>
                </form>
                <h3 style="margin-top:20px;">Current Stock</h3>
                {% for p in products %}
                <div style="background:white; padding:10px; border-radius:15px; margin-bottom:10px; display:flex; align-items:center;">
                    <img src="{{ p['img'] }}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; margin-right:10px;">
                    <span style="flex-grow:1; font-size:13px;">{{ p['name'] }}</span>
                    <a href="/delete/{{ p['id'] }}" style="color:red; font-size:12px; text-decoration:none;">Delete</a>
                </div>
                {% endfor %}
            </div>
        </body></html>
    ''', products=products)

@app.route('/add', methods=['POST'])
def add():
    if not session.get('admin'): return redirect(url_for('login'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_path = '/static/uploads/' + filename
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, img, code, desc) VALUES (?, ?, ?, ?, ?)', 
                     (request.form['n'], request.form['p'], img_path, request.form['c'], request.form['d']))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('admin'):
        conn = get_db_connection()
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
      

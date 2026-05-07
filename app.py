import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_premium_key')

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, img TEXT, code TEXT, desc TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, p_name TEXT, p_code TEXT, p_price TEXT, customer_phone TEXT, order_time TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- CSS (Ultra-Premium Styling) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;800&display=swap');
    :root { --primary: #000; --accent: #ff385c; --bg: #f7f7f7; --card-bg: #ffffff; }
    
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: var(--bg); color: #222; }
    
    /* Navigation Bar */
    .nav { position: sticky; top: 0; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); 
           border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 1000; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.4rem; text-decoration: none; color: var(--primary); letter-spacing: -1.2px; }
    .logo span { color: var(--accent); }
    .admin-btn { text-decoration: none; color: #fff; font-size: 12px; font-weight: 600; background: #222; padding: 10px 18px; border-radius: 50px; transition: 0.3s; }
    
    /* Hero Section */
    .hero { padding: 40px 24px; text-align: left; background: #fff; border-radius: 0 0 35px 35px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.02); }
    .hero h1 { font-size: 2.2rem; margin: 0; font-weight: 800; line-height: 1.1; }
    .hero p { color: #717171; font-size: 0.95rem; margin-top: 10px; }

    /* Product Grid */
    .container { padding: 0 20px 100px; }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .card { background: var(--card-bg); border-radius: 24px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); transition: transform 0.3s ease; }
    .card:active { transform: scale(0.97); }
    .card img { width: 100%; height: 210px; object-fit: cover; }
    .card-content { padding: 16px; }
    .p-code { font-size: 9px; font-weight: 700; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; }
    .p-title { font-size: 0.95rem; font-weight: 600; margin: 4px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .p-price { font-size: 1.1rem; font-weight: 800; color: var(--accent); margin-bottom: 12px; }
    
    /* Buy Form */
    .buy-input { width: 100%; padding: 10px; border-radius: 12px; border: 1.5px solid #eee; margin-bottom: 8px; font-family: inherit; font-size: 13px; outline: none; transition: 0.3s; }
    .buy-input:focus { border-color: var(--accent); }
    .btn-buy { width: 100%; background: var(--primary); color: #fff; border: none; padding: 12px; border-radius: 14px; font-weight: 700; font-size: 13px; cursor: pointer; }

    /* Admin Styles */
    .order-card { background: #fff; padding: 20px; border-radius: 20px; margin-bottom: 12px; border: 1px solid #eee; position: relative; }
    .order-tag { position: absolute; top: 15px; right: 15px; background: #e8f5e9; color: #2e7d32; font-size: 10px; padding: 4px 10px; border-radius: 50px; font-weight: 700; }
</style>
'''

# --- HOME PAGE ---
@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">''' + CSS + '''</head>
    <body>
        <nav class="nav">
            <a href="/" class="logo">KHATA<span>KHORI</span></a>
            <a href="/login" class="admin-btn">Admin</a>
        </nav>
        <div class="hero">
            <h1>Premium<br>Journal Store</h1>
            <p>Elevate your writing experience with our handcrafted journals.</p>
        </div>
        <div class="container">
            <div class="grid">
                {% for p in products %}
                <div class="card">
                    <img src="{{ p['img'] }}">
                    <div class="card-content">
                        <div class="p-code">{{ p['code'] }}</div>
                        <div class="p-title">{{ p['name'] }}</div>
                        <div class="p-price">Tk {{ p['price'] }}</div>
                        <form action="/buy" method="POST">
                            <input type="hidden" name="p_name" value="{{ p['name'] }}">
                            <input type="hidden" name="p_code" value="{{ p['code'] }}">
                            <input type="tel" name="phone" placeholder="Your Phone" class="buy-input" required>
                            <button class="btn-buy">Buy Now</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body></html>
    ''', products=products)

@app.route('/buy', methods=['POST'])
def buy():
    time = datetime.now().strftime("%d %b, %I:%M %p")
    conn = get_db_connection()
    conn.execute('INSERT INTO orders (p_name, p_code, p_price, customer_phone, order_time) VALUES (?, ?, ?, ?, ?)',
                 (request.form['p_name'], request.form['p_code'], request.form['p_price'], request.form['phone'], time))
    conn.commit()
    conn.close()
    return render_template_string('<body style="text-align:center; padding:100px; font-family:sans-serif;"><h2>Order Success!</h2><p>We will call you soon.</p><a href="/">Back</a></body>')

# --- ADMIN & DASHBOARD ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect(url_for('dashboard'))
    return render_template_string('''
    <body style="display:flex; justify-content:center; align-items:center; height:100vh; background:#f7f7f7; font-family:sans-serif;">
        <form method="POST" style="background:#fff; padding:40px; border-radius:30px; box-shadow:0 10px 40px rgba(0,0,0,0.05); width:320px;">
            <h2 style="margin-top:0;">Admin Login</h2>
            <input name="u" placeholder="Admin ID" style="width:100%; padding:15px; margin-bottom:10px; border-radius:12px; border:1px solid #eee;">
            <input name="p" type="password" placeholder="Password" style="width:100%; padding:15px; margin-bottom:20px; border-radius:12px; border:1px solid #eee;">
            <button style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:12px; font-weight:bold;">Login</button>
        </form>
    </body>''')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
    <body style="background:#f7f7f7; padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h2>Messages/Orders</h2>
            <a href="/logout" style="color:red; font-weight:600; text-decoration:none;">Logout</a>
        </div>
        
        {% for o in orders %}
        <div class="order-card">
            <span class="order-tag">NEW</span>
            <div style="font-weight:800; font-size:1.1rem; color:var(--accent);">{{ o['p_name'] }}</div>
            <div style="font-size:14px; margin:5px 0;"><b>Customer:</b> {{ o['customer_phone'] }}</div>
            <div style="font-size:12px; color:#888;">Order Time: {{ o['order_time'] }}</div>
        </div>
        {% else %}
        <p>No new messages.</p>
        {% endfor %}

        <hr style="margin:40px 0; border:0; border-top:1px solid #eee;">
        <h3>Add Product</h3>
        <form action="/add" method="POST" enctype="multipart/form-data" style="background:#fff; padding:20px; border-radius:20px;">
            <input name="n" placeholder="Product Name" class="buy-input" required>
            <input name="c" placeholder="Code (KK-01)" class="buy-input" required>
            <input name="p" placeholder="Price" class="buy-input" required>
            <input type="file" name="file" class="buy-input" required>
            <button class="btn-buy">Upload & Publish</button>
        </form>
    </body></html>
    ''', orders=orders, products=products)

@app.route('/add', methods=['POST'])
def add():
    if not session.get('admin'): return redirect(url_for('login'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_url = '/static/uploads/' + filename
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, img, code) VALUES (?, ?, ?, ?)', 
                     (request.form['n'], request.form['p'], img_url, request.form['c']))
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

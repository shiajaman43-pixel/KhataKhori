import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_order_system_secret')

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
    # Product Table
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, price TEXT, img TEXT, 
                     code TEXT, desc TEXT)''')
    # Order Table
    conn.execute('''CREATE TABLE IF NOT EXISTS orders 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     p_name TEXT, p_code TEXT, p_price TEXT,
                     customer_phone TEXT, order_time TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- CSS (Premium UI) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #fff; }
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.85); backdrop-filter: blur(15px); border-bottom: 1px solid #eee; z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; text-decoration: none; color: #000; }
    .logo span { color: var(--accent); }
    .admin-link { text-decoration: none; color: #111; font-size: 13px; font-weight: 600; background: var(--gray); padding: 8px 15px; border-radius: 50px; border: 1px solid #ddd; }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 20px; }
    .card { background: #fff; border-radius: 20px; border: 1px solid #eee; overflow: hidden; }
    .card img { width: 100%; height: 180px; object-fit: cover; }
    .btn { width: 100%; padding: 12px; border-radius: 12px; border: none; font-weight: bold; cursor: pointer; }
    .order-card { background: #fff; padding: 15px; border-radius: 15px; border-left: 5px solid var(--accent); margin-bottom: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.02); }
</style>
'''

# --- PAGES ---

@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
    <body>
        <nav class="nav">
            <a href="/" class="logo">KHATA<span>KHORI</span></a>
            <a href="/login" class="admin-link">Admin Panel</a>
        </nav>
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['img'] }}">
                <div style="padding:12px; text-align:center;">
                    <small style="color:#999;">{{ p['code'] }}</small>
                    <h4 style="margin:5px 0;">{{ p['name'] }}</h4>
                    <p style="color:var(--accent); font-weight:800; margin-bottom:10px;">Tk. {{ p['price'] }}</p>
                    <form action="/buy" method="POST">
                        <input type="hidden" name="p_name" value="{{ p['name'] }}">
                        <input type="hidden" name="p_code" value="{{ p['code'] }}">
                        <input type="hidden" name="p_price" value="{{ p['price'] }}">
                        <input type="text" name="phone" placeholder="Phone Number" required style="width:100%; padding:8px; border-radius:8px; border:1px solid #ddd; margin-bottom:8px; font-size:12px;">
                        <button class="btn" style="background:#000; color:#fff; font-size:12px;">Buy Now</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </body></html>
    ''', products=products)

@app.route('/buy', methods=['POST'])
def buy():
    p_name = request.form['p_name']
    p_code = request.form['p_code']
    p_price = request.form['p_price']
    phone = request.form['phone']
    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_db_connection()
    conn.execute('INSERT INTO orders (p_name, p_code, p_price, customer_phone, order_time) VALUES (?, ?, ?, ?, ?)',
                 (p_name, p_code, p_price, phone, time))
    conn.commit()
    conn.close()
    return "<h1>Order Successful!</h1><p>We will contact you soon.</p><a href='/'>Back to Home</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect(url_for('dashboard'))
    return render_template_string('<body style="padding:50px; text-align:center;"><form method="POST"><h2>Login</h2><input name="u" placeholder="User"><br><input name="p" type="password" placeholder="Pass"><br><button>Login</button></form></body>')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
    <body style="background:var(--gray); padding:20px;">
        <h2>Admin Dashboard <a href="/logout" style="font-size:12px; color:red;">Logout</a></h2>
        
        <h3 style="color:var(--accent);">New Orders (Messages)</h3>
        {% for o in orders %}
        <div class="order-card">
            <b>Product:</b> {{ o['p_name'] }} ({{ o['p_code'] }})<br>
            <b>Customer Phone:</b> <span style="color:blue;">{{ o['customer_phone'] }}</span><br>
            <b>Time:</b> <small>{{ o['order_time'] }}</small>
        </div>
        {% else %}
        <p>No orders yet.</p>
        {% endfor %}

        <hr>
        <h3>Add New Product</h3>
        <form action="/add" method="POST" enctype="multipart/form-data">
            <input name="n" placeholder="Product Name" required><br>
            <input name="c" placeholder="Code" required><br>
            <input name="p" placeholder="Price" required><br>
            <input type="file" name="file" required><br>
            <button class="btn" style="background:#000; color:#fff;">Publish</button>
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
  

import sqlite3
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'arsvim_v1_secret_key' # Render-e deploy korle eti joruri

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, img TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- PREMIUM CSS (Khatakhori Style) ---
CSS = '''
<style>
    :root { --primary: #222; --accent: #ff4d4d; --bg: #fdfdfd; }
    body { font-family: 'Poppins', sans-serif; background: var(--bg); color: var(--primary); margin: 0; }
    .navbar { background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); padding: 15px 0; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; }
    .navbar-brand { font-weight: 800; letter-spacing: 2px; text-decoration: none; color: var(--primary); font-size: 1.2rem; }
    .hero { padding: 60px 0; text-align: center; background: #fff; border-bottom: 1px solid #f9f9f9; }
    .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 20px; }
    @media (min-width: 768px) { .product-grid { grid-template-columns: repeat(4, 1fr); } }
    .card { background: white; border-radius: 15px; overflow: hidden; transition: 0.4s; border: 1px solid #f1f1f1; position: relative; }
    .card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.05); }
    .card img { width: 100%; height: 220px; object-fit: cover; background: #f9f9f9; }
    .info { padding: 12px; text-align: center; }
    .info h6 { margin: 5px 0; font-weight: 500; font-size: 0.95rem; }
    .price { color: var(--accent); font-weight: 700; font-size: 0.9rem; }
    .btn-buy { background: var(--primary); color: white; border: none; padding: 8px 15px; border-radius: 20px; width: 100%; font-size: 0.8rem; cursor: pointer; transition: 0.3s; }
    .btn-buy:hover { opacity: 0.8; }
    .admin-login-link { position: fixed; bottom: 20px; right: 20px; background: #eee; padding: 8px 12px; border-radius: 50px; text-decoration: none; font-size: 12px; color: #777; }
</style>
'''

# --- HTML TEMPLATES ---

# 1. Home Page
HOME_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;800&display=swap" rel="stylesheet">
    ''' + CSS + '''
</head>
<body>
    <nav class="navbar">
        <div style="width: 90%; margin: auto; display: flex; justify-content: space-between; align-items: center;">
            <a href="/" class="navbar-brand">KHATA<span style="color:var(--accent)">KHORI</span></a>
            <div style="font-weight: 500;">Cart (0)</div>
        </div>
    </nav>

    <div class="hero">
        <h1 style="margin:0; font-weight:800;">Elevate Your Journaling</h1>
        <p style="color:#888;">Premium handcrafted stationery for your creative soul.</p>
    </div>

    <div class="product-grid">
        {% for p in products %}
        <div class="card">
            <img src="{{ p[3] }}" alt="product">
            <div class="info">
                <h6>{{ p[1] }}</h6>
                <p class="price">Tk. {{ p[2] }}</p>
                <button class="btn-buy">Add to Cart</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <a href="/login" class="admin-login-link">Admin Access</a>
</body>
</html>
'''

# (Login & Dashboard HTML template-gulo ager motoi thakbe, sudhu look refresh kora)

# --- ROUTES ---

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    items = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template_string(HOME_HTML, products=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['pass'] == '12345':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template_string('''
        <body style="font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; background:#f5f5f5;">
            <form method="POST" style="background:#fff; padding:30px; border-radius:15px; box-shadow:0 10px 20px rgba(0,0,0,0.05);">
                <h3>Admin Login</h3>
                <input name="user" placeholder="User" style="display:block; margin-bottom:10px; padding:10px; width:200px;">
                <input name="pass" type="password" placeholder="Pass" style="display:block; margin-bottom:10px; padding:10px; width:200px;">
                <button style="width:100%; padding:10px; background:#222; color:#fff; border:none; border-radius:5px;">Login</button>
            </form>
        </body>
    ''')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    return render_template_string('''
        <body style="font-family:sans-serif; padding:20px;">
            <h2>Admin Dashboard</h2>
            <form action="/add" method="POST" style="margin-bottom:30px; background:#eee; padding:20px; border-radius:10px;">
                <input name="n" placeholder="Product Name" required>
                <input name="p" placeholder="Price" required>
                <input name="i" placeholder="Image URL" required>
                <button>Add Product</button>
            </form>
            <a href="/logout">Logout</a>
        </body>
    ''')

@app.route('/add', methods=['POST'])
def add():
    if session.get('admin'):
        conn = sqlite3.connect('database.db')
        conn.execute('INSERT INTO products (name, price, img) VALUES (?, ?, ?)', 
                     (request.form['n'], request.form['p'], request.form['i']))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

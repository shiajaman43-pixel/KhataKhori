import sqlite3
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_ultra_secret')

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      name TEXT, price TEXT, img TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- ULTRA PREMIUM CSS (Clean & Mobile First) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; --border: #eee; }
    
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; outline: none; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: #fff; color: var(--primary); margin: 0; }
    
    /* Global Styles */
    .container { max-width: 1200px; margin: auto; padding: 0 15px; }
    a { text-decoration: none; color: inherit; }

    /* Navbar */
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.8); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; letter-spacing: -1px; }
    .logo span { color: var(--accent); }

    /* Hero Section */
    .hero { padding: 50px 20px; background: var(--gray); border-radius: 0 0 40px 40px; margin-bottom: 30px; }
    .hero h1 { font-size: 2.5rem; line-height: 1; margin: 0; font-weight: 800; }
    .hero p { color: #666; margin-top: 15px; font-size: 0.95rem; }

    /* Modern Grid */
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 0 15px 50px; }
    @media (min-width: 768px) { .grid { grid-template-columns: repeat(4, 1fr); } }

    /* Product Card */
    .card { background: #fff; border-radius: 24px; overflow: hidden; border: 1px solid var(--border); position: relative; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .card:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
    .img-box { position: relative; width: 100%; height: 240px; background: #f0f0f0; }
    .img-box img { width: 100%; height: 100%; object-fit: cover; transition: 0.5s; }
    .badge { position: absolute; top: 12px; left: 12px; background: rgba(0,0,0,0.8); color: #fff; padding: 5px 12px; border-radius: 50px; font-size: 10px; font-weight: 700; text-transform: uppercase; }

    .card-info { padding: 15px; }
    .name { font-size: 0.9rem; font-weight: 500; color: #444; margin: 0; }
    .price { font-weight: 800; color: var(--accent); font-size: 1.1rem; margin: 8px 0; }
    .btn-buy { width: 100%; padding: 12px; background: var(--primary); color: #fff; border: none; border-radius: 15px; font-size: 0.85rem; font-weight: 700; cursor: pointer; }

    /* Admin Styles */
    .admin-form { background: var(--gray); padding: 25px; border-radius: 30px; margin-bottom: 30px; border: 1px solid #eee; }
    .form-input { width: 100%; padding: 15px; margin-bottom: 12px; border: 1px solid #ddd; border-radius: 12px; background: #fff; }
    .admin-list-item { display: flex; align-items: center; background: #fff; padding: 15px; border-radius: 20px; margin-bottom: 12px; border: 1px solid var(--border); }
    .admin-list-item img { width: 60px; height: 60px; border-radius: 12px; object-fit: cover; margin-right: 15px; }
    .btn-stock { background: #eef2ff; color: #4338ca; padding: 8px 15px; border-radius: 10px; font-size: 12px; font-weight: 600; }
    .btn-del { background: #fff1f2; color: #e11d48; padding: 8px 15px; border-radius: 10px; font-size: 12px; font-weight: 600; margin-left: 10px; }
</style>
'''

# --- PAGES ---

HOME_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body>
    <nav class="nav">
        <a href="/" class="logo">KHATA<span>KHORI</span></a>
        <div style="background: var(--primary); color: #fff; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 12px;">0</div>
    </nav>
    
    <div class="hero container">
        <h1>Handmade<br>Storytelling.</h1>
        <p>Premium quality tools for your creative journey. Designed with simplicity in mind.</p>
    </div>

    <div class="grid container">
        {% for p in products %}
        <div class="card">
            {% if p[4] == 0 %}<div class="badge">Sold Out</div>{% endif %}
            <div class="img-box">
                <img src="{{ p[3] }}" style="{{ 'filter:grayscale(1); opacity:0.5;' if p[4] == 0 }}">
            </div>
            <div class="card-info">
                <p class="name">{{ p[1] }}</p>
                <p class="price">Tk. {{ p[2] }}</p>
                <button class="btn-buy" {{ 'disabled style="background:#ccc"' if p[4] == 0 }}>{{ 'Out of Stock' if p[4] == 0 else 'Add to Bag' }}</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <div style="text-align:center; padding:60px 20px; border-top: 1px solid #eee; color: #aaa; font-size: 12px;">
        <a href="/login" style="margin-bottom: 20px; display: block;">Admin Login</a>
        &copy; 2026 KHATA KHORI • ESTD IN BANGLADESH
    </div>
</body></html>
'''

ADMIN_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body style="background:#fcfcfc;">
    <nav class="nav">
        <span class="logo">DASH<span>BOARD</span></span>
        <a href="/logout" style="font-weight:700; font-size: 14px; color: var(--accent);">Sign Out</a>
    </nav>
    <div class="container" style="padding-top: 30px;">
        <div class="admin-form">
            <h2 style="margin-top:0; font-size: 1.5rem;">New Arrival</h2>
            <form action="/add" method="POST">
                <input name="n" class="form-input" placeholder="Product Name" required>
                <input name="p" class="form-input" placeholder="Price (Tk)" type="number" required>
                <input name="i" class="form-input" placeholder="Direct Image URL (.jpg / .png)" required>
                <button style="width:100%; padding:18px; background:var(--primary); color:#fff; border:none; border-radius:15px; font-weight:800; cursor:pointer;">List Product</button>
            </form>
        </div>

        <h3 style="margin-bottom:20px;">Inventory Control</h3>
        {% for p in products %}
        <div class="admin-list-item">
            <img src="{{ p[3] }}">
            <div style="flex-grow: 1;">
                <div style="font-weight:700; font-size: 14px;">{{ p[1] }}</div>
                <div style="font-size:12px; color:#888;">{{ p[2] }} Tk • {{ 'Live' if p[4] == 1 else 'Hidden' }}</div>
            </div>
            <div>
                <a href="/toggle_stock/{{ p[0] }}" class="btn-stock">Stock</a>
                <a href="/delete/{{ p[0] }}" class="btn-del" onclick="return confirm('Remove permanently?')">Del</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body></html>
'''

# --- BACKEND LOGIC ---

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    items = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string(HOME_HTML, products=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template_string('<body style="font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; background:#f4f4f4;"><form method="POST" style="background:#fff; padding:40px; border-radius:30px; box-shadow:0 20px 60px rgba(0,0,0,0.05); width:320px;"><h2 style="margin-top:0; font-weight:800;">Log In</h2><input name="u" placeholder="Admin ID" style="width:100%; padding:15px; margin-bottom:12px; border:1px solid #ddd; border-radius:12px;"><input name="p" type="password" placeholder="Password" style="width:100%; padding:15px; margin-bottom:25px; border:1px solid #ddd; border-radius:12px;"><button style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:12px; font-weight:bold; cursor:pointer;">Authenticate</button></form></body>')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    conn = sqlite3.connect('database.db')
    items = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string(ADMIN_HTML, products=items)

@app.route('/add', methods=['POST'])
def add():
    if session.get('admin'):
        conn = sqlite3.connect('database.db')
        conn.execute('INSERT INTO products (name, price, img, stock) VALUES (?, ?, ?, 1)', 
                     (request.form['n'], request.form['p'], request.form['i']))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('admin'):
        conn = sqlite3.connect('database.db')
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/toggle_stock/<int:id>')
def toggle_stock(id):
    if session.get('admin'):
        conn = sqlite3.connect('database.db')
        conn.execute('UPDATE products SET stock = 1 - stock WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
          

import os
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_secret')

# --- DATABASE SETUP ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, price TEXT, img TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- PREMIUM MOBILE UI (KhataKhori Style) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #fff; color: var(--primary); -webkit-font-smoothing: antialiased; }
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.8); backdrop-filter: blur(15px); border-bottom: 1px solid #eee; z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; text-decoration: none; color: #000; letter-spacing: -1px; }
    .logo span { color: var(--accent); }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 20px; }
    .card { background: #fff; border-radius: 20px; border: 1px solid #eee; overflow: hidden; position: relative; transition: 0.3s; }
    .card img { width: 100%; height: 220px; object-fit: cover; }
    .badge { position: absolute; top: 10px; left: 10px; background: #000; color: #fff; padding: 4px 10px; border-radius: 50px; font-size: 9px; font-weight: bold; }
    .card-info { padding: 12px; text-align: center; }
    .price { color: var(--accent); font-weight: 800; margin: 5px 0; }
    .btn-buy { width:100%; background:#111; color:#fff; border:none; padding:10px; border-radius:12px; font-size:0.8rem; font-weight:600; cursor:pointer; }
</style>
'''

HOME_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body>
    <nav class="nav"><a href="/" class="logo">KHATA<span>KHORI</span></a><div style="font-size:14px; font-weight:600;">Bag (0)</div></nav>
    <div style="padding:40px 20px; background:var(--gray); text-align:center; border-radius:0 0 40px 40px;">
        <h1 style="margin:0; font-size:2.2rem; font-weight:800;">Premium Journals</h1>
        <p style="color:#666; font-size:0.9rem;">Handcrafted with love in Bangladesh</p>
    </div>
    <div class="grid">
        {% for p in products %}
        <div class="card">
            {% if p['stock'] == 0 %}<div class="badge">SOLD OUT</div>{% endif %}
            <img src="{{ p['img'] }}" style="{{ 'filter:grayscale(1); opacity:0.5;' if p['stock'] == 0 }}">
            <div class="card-info">
                <p style="font-size: 0.85rem; margin: 0; color:#555;">{{ p['name'] }}</p>
                <p class="price">Tk. {{ p['price'] }}</p>
                <button class="btn-buy">Add to Bag</button>
            </div>
        </div>
        {% endfor %}
    </div>
    <div style="text-align:center; padding:40px; color:#aaa; font-size:10px;"><a href="/login" style="color:#aaa;">Admin Access</a></div>
</body></html>
'''

# --- ROUTES ---

@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string(HOME_HTML, products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template_string('<body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;background:#f4f4f4;"><form method="POST" style="padding:40px;background:#fff;border-radius:25px;box-shadow:0 10px 40px rgba(0,0,0,0.05);"><h2 style="margin-top:0;">Login</h2><input name="u" placeholder="Admin ID" style="display:block;width:100%;padding:12px;margin-bottom:10px;border-radius:10px;border:1px solid #ddd;"><input name="p" type="password" placeholder="Pass" style="display:block;width:100%;padding:12px;margin-bottom:20px;border-radius:10px;border:1px solid #ddd;"><button style="width:100%;padding:12px;background:#000;color:#fff;border:none;border-radius:10px;font-weight:bold;">Login</button></form></body>')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
        <body style="background:#f8f9fa; padding:20px;">
            <div style="max-width:500px; margin:auto;">
                <h2 style="display:flex; justify-content:space-between;">Admin <a href="/logout" style="font-size:14px; color:red;">Logout</a></h2>
                <form action="/add" method="POST" style="background:#fff; padding:20px; border-radius:20px; margin-bottom:20px; box-shadow:0 5px 15px rgba(0,0,0,0.03);">
                    <input name="n" placeholder="Product Name" style="width:100%; padding:12px; margin-bottom:10px; border-radius:10px; border:1px solid #eee;" required>
                    <input name="p" placeholder="Price" style="width:100%; padding:12px; margin-bottom:10px; border-radius:10px; border:1px solid #eee;" required>
                    <input name="i" placeholder="Pinterest Image URL" style="width:100%; padding:12px; margin-bottom:10px; border-radius:10px; border:1px solid #eee;" required>
                    <button style="width:100%; padding:15px; background:#111; color:#fff; border:none; border-radius:12px; font-weight:bold;">Add Product</button>
                </form>
                {% for p in products %}
                <div style="background:#fff; padding:10px; border-radius:15px; margin-bottom:10px; display:flex; align-items:center; border:1px solid #eee;">
                    <img src="{{ p['img'] }}" style="width:50px; height:50px; border-radius:10px; object-fit:cover; margin-right:15px;">
                    <div style="flex-grow:1;"><b style="font-size:14px;">{{ p['name'] }}</b><br><small>{{ p['price'] }} Tk</small></div>
                    <a href="/toggle_stock/{{ p['id'] }}" style="font-size:11px; background:#eee; padding:5px 8px; border-radius:5px; text-decoration:none; color:#000;">Stock</a>
                    <a href="/delete/{{ p['id'] }}" style="font-size:11px; color:red; margin-left:10px;" onclick="return confirm('Delete?')">Del</a>
                </div>
                {% endfor %}
            </div>
        </body></html>
    ''', products=products)

@app.route('/add', methods=['POST'])
def add():
    if session.get('admin'):
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, img) VALUES (?, ?, ?)', (request.form['n'], request.form['p'], request.form['i']))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('admin'):
        conn = get_db_connection()
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/toggle_stock/<int:id>')
def toggle_stock(id):
    if session.get('admin'):
        conn = get_db_connection()
        conn.execute('UPDATE products SET stock = 1 - stock WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  

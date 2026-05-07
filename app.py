import sqlite3
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'arsvim_v1_ultra_premium'

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

# --- ULTRA PREMIUM CSS (Khatakhori Mobile Style) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&display=swap');
    :root { --primary: #121212; --accent: #e63946; --soft-bg: #f8f9fa; --glass: rgba(255, 255, 255, 0.8); }
    
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: #fff; color: var(--primary); margin: 0; overflow-x: hidden; }
    
    /* Navbar */
    .nav { position: sticky; top: 0; background: var(--glass); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(0,0,0,0.05); z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.2rem; letter-spacing: -0.5px; text-decoration: none; color: var(--primary); }
    .logo span { color: var(--accent); }

    /* Hero */
    .hero { padding: 40px 20px; background: linear-gradient(180deg, #fff 0%, var(--soft-bg) 100%); text-align: left; }
    .hero h1 { font-size: 2.2rem; line-height: 1.1; margin: 0; font-weight: 800; }
    .hero p { color: #666; font-size: 0.95rem; margin-top: 10px; }

    /* Product Grid */
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 15px; }
    .item { background: #fff; border-radius: 20px; overflow: hidden; border: 1px solid #f1f1f1; position: relative; transition: 0.3s; }
    .img-box { position: relative; width: 100%; height: 220px; }
    .img-box img { width: 100%; height: 100%; object-fit: cover; }
    .out-badge { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: #fff; padding: 4px 10px; border-radius: 50px; font-size: 9px; font-weight: 600; }
    .item-info { padding: 12px; }
    .item-name { font-size: 0.85rem; font-weight: 500; margin: 0; color: #333; height: 2.4em; overflow: hidden; }
    .item-price { font-weight: 800; color: var(--accent); margin: 5px 0; font-size: 0.95rem; }
    
    /* Improved Admin Panel */
    .admin-container { padding: 20px; max-width: 600px; margin: auto; }
    .input-group { background: #fff; border: 1px solid #ddd; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); }
    .form-input { width: 100%; padding: 12px; margin-bottom: 10px; border: 1px solid #eee; border-radius: 10px; font-family: inherit; }
    .admin-card { display: flex; align-items: center; background: #fff; padding: 12px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #f1f1f1; }
    .admin-card img { width: 50px; height: 50px; border-radius: 10px; object-fit: cover; margin-right: 15px; }
    .actions { margin-left: auto; display: flex; gap: 5px; }
    .btn-act { padding: 8px; border-radius: 8px; border: none; font-size: 11px; cursor: pointer; font-weight: 600; }
    .del { background: #ffe5e5; color: #e63946; }
    .stk { background: #eef2ff; color: #4f46e5; }
</style>
'''

# --- HOME TEMPLATE ---
HOME_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body>
    <nav class="nav">
        <a href="/" class="logo">KHATA<span>KHORI</span></a>
        <div style="font-weight: 600; font-size: 0.9rem;">Cart (0)</div>
    </nav>
    <div class="hero">
        <h1>Handcrafted Essentials</h1>
        <p>Premium notebooks & stationery for your creative space.</p>
    </div>
    <div class="grid">
        {% for p in products %}
        <div class="item">
            {% if p[4] == 0 %}<div class="out-badge">OUT OF STOCK</div>{% endif %}
            <div class="img-box">
                <img src="{{ p[3] }}" style="{{ 'filter:grayscale(1); opacity:0.6;' if p[4] == 0 }}">
            </div>
            <div class="item-info">
                <p class="item-name">{{ p[1] }}</p>
                <p class="item-price">Tk. {{ p[2] }}</p>
                <button style="width:100%; background:#121212; color:#fff; border:none; padding:8px; border-radius:12px; font-size:0.8rem; font-weight:600;">Add to Cart</button>
            </div>
        </div>
        {% endfor %}
    </div>
    <div style="text-align:center; padding:40px; background:#f9f9f9; color:#999; font-size:0.7rem;">
        <a href="/login" style="color:#999; text-decoration:none;">Admin Access</a><br><br>
        &copy; 2026 KHATA KHORI CLONE
    </div>
</body></html>
'''

# --- ADMIN DASHBOARD TEMPLATE ---
ADMIN_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body style="background:#f8f9fa;">
    <nav class="nav">
        <span class="logo">ADMIN<span>PANEL</span></span>
        <a href="/logout" style="text-decoration:none; color:#666; font-size:0.8rem;">Logout</a>
    </nav>
    <div class="admin-container">
        <div class="input-group">
            <h3 style="margin-top:0;">Add Product</h3>
            <form action="/add" method="POST">
                <input name="n" class="form-input" placeholder="Product Name" required>
                <input name="p" class="form-input" placeholder="Price (Tk)" type="number" required>
                <input name="i" class="form-input" placeholder="Image Link (URL)" required>
                <button style="width:100%; padding:12px; background:#121212; color:#fff; border:none; border-radius:10px; font-weight:bold;">Publish Product</button>
            </form>
        </div>

        <h3 style="margin-left:5px;">Manage Inventory ({{ products|length }})</h3>
        {% for p in products %}
        <div class="admin-card">
            <img src="{{ p[3] }}">
            <div>
                <div style="font-weight:600; font-size:0.9rem;">{{ p[1] }}</div>
                <div style="font-size:0.8rem; color:#888;">{{ p[2] }} Tk • {{ 'In Stock' if p[4] == 1 else 'Out' }}</div>
            </div>
            <div class="actions">
                <a href="/toggle_stock/{{ p[0] }}" class="btn-act stk" style="text-decoration:none;">Stock</a>
                <a href="/delete/{{ p[0] }}" class="btn-act del" style="text-decoration:none;" onclick="return confirm('Delete this item?')">Delete</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body></html>
'''

# --- ROUTES ---
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
    return render_template_string('<body style="font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; background:#f4f4f4;"><form method="POST" style="background:#fff; padding:40px; border-radius:20px; box-shadow:0 10px 40px rgba(0,0,0,0.05); width:300px;"><h2 style="margin-top:0;">Login</h2><input name="u" placeholder="User" style="width:100%; padding:12px; margin-bottom:10px; border:1px solid #ddd; border-radius:10px;"><input name="p" type="password" placeholder="Pass" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #ddd; border-radius:10px;"><button style="width:100%; padding:12px; background:#000; color:#fff; border:none; border-radius:10px; font-weight:bold;">Enter Dashboard</button></form></body>')

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
    app.run(host='0.0.0.0', port=5000)

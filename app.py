import sqlite3
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'arsvim_v1_premium_key'

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # 'stock' column add kora hoyeche (1 = In Stock, 0 = Out of Stock)
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      name TEXT, price TEXT, img TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- PREMIUM CSS ---
CSS = '''
<style>
    :root { --primary: #222; --accent: #ff4d4d; --bg: #fdfdfd; }
    body { font-family: 'Poppins', sans-serif; background: var(--bg); color: var(--primary); margin: 0; }
    .navbar { background: rgba(255,255,255,0.85); backdrop-filter: blur(12px); padding: 15px 0; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; }
    .navbar-brand { font-weight: 800; letter-spacing: 2px; text-decoration: none; color: var(--primary); font-size: 1.2rem; margin-left: 5%; }
    .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 20px; max-width: 1200px; margin: auto; }
    .card { background: white; border-radius: 15px; overflow: hidden; border: 1px solid #f1f1f1; position: relative; }
    .card img { width: 100%; height: 200px; object-fit: cover; filter: brightness(1); }
    .out-of-stock-img { filter: grayscale(1) brightness(0.5) !important; }
    .stock-badge { position: absolute; top: 10px; right: 10px; background: var(--accent); color: white; padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: bold; }
    .info { padding: 12px; text-align: center; }
    .price { color: var(--accent); font-weight: 700; }
    .admin-table { width: 90%; margin: 20px auto; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
    .admin-table th, .admin-table td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
    .btn { padding: 6px 12px; border-radius: 5px; border: none; cursor: pointer; text-decoration: none; font-size: 12px; }
    .btn-del { background: #ff4d4d; color: white; }
    .btn-stock { background: #555; color: white; }
</style>
'''

# --- ROUTES ---

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    items = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template_string('''
        <html><head>''' + CSS + '''</head><body>
        <nav class="navbar"><a href="/" class="navbar-brand">KHATA<span style="color:var(--accent)">KHORI</span></a></nav>
        <div class="product-grid">
            {% for p in products %}
            <div class="card">
                {% if p[4] == 0 %}<div class="stock-badge">OUT OF STOCK</div>{% endif %}
                <img src="{{ p[3] }}" class="{{ 'out-of-stock-img' if p[4] == 0 }}">
                <div class="info">
                    <h6>{{ p[1] }}</h6>
                    <p class="price">Tk. {{ p[2] }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
        </body></html>
    ''', products=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['pass'] == '12345':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template_string('<body style="text-align:center;padding-top:100px;"><form method="POST"><h3>Admin</h3><input name="user" placeholder="User"><br><input name="pass" type="password" placeholder="Pass"><br><button>Login</button></form></body>')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    conn = sqlite3.connect('database.db')
    items = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template_string('''
        <html><head>''' + CSS + '''</head><body>
        <div style="padding:20px;">
            <h2>Admin Dashboard <a href="/logout" style="font-size:14px;">Logout</a></h2>
            <form action="/add" method="POST" style="background:#eee; padding:20px; border-radius:10px;">
                <input name="n" placeholder="Product Name" required>
                <input name="p" placeholder="Price" required>
                <input name="i" placeholder="Image URL" required>
                <button class="btn" style="background:#222; color:#white;">Add Product</button>
            </form>
            <table class="admin-table">
                <tr><th>Product</th><th>Price</th><th>Stock</th><th>Action</th></tr>
                {% for p in products %}
                <tr>
                    <td>{{ p[1] }}</td>
                    <td>{{ p[2] }} Tk</td>
                    <td>{{ 'In Stock' if p[4] == 1 else 'Out of Stock' }}</td>
                    <td>
                        <a href="/toggle_stock/{{ p[0] }}" class="btn btn-stock">Toggle Stock</a>
                        <a href="/delete/{{ p[0] }}" class="btn btn-del" onclick="return confirm('Sure?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        </body></html>
    ''', products=items)

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
def delete_product(id):
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
        # Current stock status check kore reverse kore dibe (1 hole 0, 0 hole 1)
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
      

import os
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_final_secret')

# --- CONFIGURATION ---
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

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, price TEXT, img TEXT, 
                     code TEXT, desc TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- CSS (Premium Minimalist UI) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #fff; color: var(--primary); }
    
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.85); backdrop-filter: blur(15px); border-bottom: 1px solid #eee; z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; text-decoration: none; color: #000; letter-spacing: -1px; }
    .logo span { color: var(--accent); }
    
    .admin-link { text-decoration: none; color: #111; font-size: 13px; font-weight: 600; background: var(--gray); padding: 8px 15px; border-radius: 50px; border: 1px solid #ddd; }
    
    .container { max-width: 800px; margin: auto; padding: 20px; }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
    .card { background: #fff; border-radius: 20px; border: 1px solid #eee; overflow: hidden; position: relative; }
    .card img { width: 100%; height: 200px; object-fit: cover; }
    .card-info { padding: 12px; text-align: center; }
    .price { color: var(--accent); font-weight: 800; margin: 5px 0; }
    .p-code { font-size: 10px; color: #999; text-transform: uppercase; margin-bottom: 5px; }
    .btn { width: 100%; padding: 12px; border-radius: 12px; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
    input, textarea { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 10px; border: 1px solid #ddd; font-family: inherit; }
</style>
'''

# --- HOME PAGE ---
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
        <div class="container">
            <div class="grid">
                {% for p in products %}
                <div class="card">
                    <img src="{{ p['img'] }}">
                    <div class="card-info">
                        <div class="p-code">{{ p['code'] }}</div>
                        <p style="font-size: 0.9rem; margin: 0; font-weight:600;">{{ p['name'] }}</p>
                        <p class="price">Tk. {{ p['price'] }}</p>
                        <p style="font-size: 11px; color:#777; margin-bottom:10px;">{{ p['desc'] }}</p>
                        <button class="btn" style="background:#111; color:#fff;">Add to Bag</button>
                    </div>
                </div>
                {% else %}
                <div style="grid-column: span 2; text-align: center; padding: 100px 0; color: #bbb;">
                    No products listed yet. Click Admin Panel to add.
                </div>
                {% endfor %}
            </div>
        </div>
    </body></html>
    ''', products=products)

# --- LOGIN PAGE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect(url_for('dashboard'))
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
    <body style="display:flex; justify-content:center; align-items:center; height:100vh; background:var(--gray);">
        <form method="POST" style="background:#fff; padding:30px; border-radius:25px; box-shadow:0 10px 40px rgba(0,0,0,0.05); width:320px;">
            <h2 style="margin-top:0;">Admin Access</h2>
            <input name="u" placeholder="Admin ID" required>
            <input name="p" type="password" placeholder="Password" required>
            <button class="btn" style="background:#000; color:#fff;">Login</button>
            <br><br><center><a href="/" style="font-size:12px; color:#888;">Back to Home</a></center>
        </form>
    </body></html>
    ''')

# --- DASHBOARD PAGE ---
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
    <body style="background:var(--gray);">
        <nav class="nav">
            <span class="logo">DASH<span>BOARD</span></span>
            <a href="/logout" style="color:red; text-decoration:none; font-weight:600; font-size:13px;">Logout</a>
        </nav>
        <div class="container">
            <div style="background:#fff; padding:25px; border-radius:25px; border:1px solid #eee; margin-bottom:30px;">
                <h3 style="margin-top:0;">Add New Product</h3>
                <form action="/add" method="POST" enctype="multipart/form-data">
                    <input name="n" placeholder="Product Name" required>
                    <input name="c" placeholder="Product Code (e.g. KK-001)" required>
                    <input name="p" placeholder="Price (Tk)" type="number" required>
                    <textarea name="d" placeholder="Short Description..."></textarea>
                    <label style="font-size:12px; font-weight:600; display:block; margin-bottom:5px;">Select Gallery Image:</label>
                    <input type="file" name="file" accept="image/*" required>
                    <button class="btn" style="background:#000; color:#fff;">Upload & Publish</button>
                </form>
            </div>
            
            <h3>Current Inventory</h3>
            {% for p in products %}
            <div style="background:#fff; padding:10px; border-radius:15px; margin-bottom:10px; display:flex; align-items:center; border:1px solid #eee;">
                <img src="{{ p['img'] }}" style="width:50px; height:50px; border-radius:10px; object-fit:cover; margin-right:15px;">
                <div style="flex-grow:1;">
                    <b style="font-size:14px;">{{ p['name'] }}</b><br>
                    <small>{{ p['code'] }} • {{ p['price'] }} Tk</small>
                </div>
                <a href="/delete/{{ p['id'] }}" style="color:red; font-size:12px; text-decoration:none;" onclick="return confirm('Delete?')">Delete</a>
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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        img_url = '/static/uploads/' + filename
        
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, img, code, desc) VALUES (?, ?, ?, ?, ?)', 
                     (request.form['n'], request.form['p'], img_url, request.form['c'], request.form['d']))
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

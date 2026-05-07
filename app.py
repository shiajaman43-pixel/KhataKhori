import os
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_final_key')

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Database update: 'code' ebong 'desc' column add kora hoyeche
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, price TEXT, img TEXT, 
                     code TEXT, desc TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- CSS (Premium & Clean) ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #fff; color: var(--primary); }
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.85); backdrop-filter: blur(15px); border-bottom: 1px solid #eee; z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; text-decoration: none; color: #000; }
    .logo span { color: var(--accent); }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 20px; }
    .card { background: #fff; border-radius: 20px; border: 1px solid #eee; overflow: hidden; position: relative; }
    .card img { width: 100%; height: 200px; object-fit: cover; }
    .card-info { padding: 12px; text-align: center; }
    .price { color: var(--accent); font-weight: 800; margin: 5px 0; }
    .p-code { font-size: 10px; color: #999; text-transform: uppercase; margin-bottom: 5px; }
    
    /* Admin Form Style */
    .admin-form { background: #fff; padding: 25px; border-radius: 25px; border: 1px solid #eee; margin-bottom: 30px; }
    .input-field { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 10px; border: 1px solid #ddd; font-family: inherit; }
    .textarea-field { width: 100%; padding: 12px; height: 80px; margin-bottom: 10px; border-radius: 10px; border: 1px solid #ddd; font-family: inherit; }
</style>
'''

# --- HOME UI ---
HOME_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body>
    <nav class="nav"><a href="/" class="logo">KHATA<span>KHORI</span></a></nav>
    <div class="grid">
        {% for p in products %}
        <div class="card">
            <img src="{{ p['img'] }}">
            <div class="card-info">
                <div class="p-code">Code: {{ p['code'] }}</div>
                <p style="font-size: 0.85rem; margin: 0; font-weight:600;">{{ p['name'] }}</p>
                <p class="price">Tk. {{ p['price'] }}</p>
                <p style="font-size: 11px; color:#777; margin-bottom:10px;">{{ p['desc'] }}</p>
                <button style="width:100%; background:#111; color:#fff; border:none; padding:10px; border-radius:12px; font-weight:600;">Add to Bag</button>
            </div>
        </div>
        {% endfor %}
    </div>
</body></html>
'''

# --- ADMIN PANEL UI ---
ADMIN_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body style="background: var(--gray); padding:20px;">
    <div style="max-width:500px; margin:auto;">
        <div class="admin-form">
            <h2 style="margin-top:0;">Add New Arrival</h2>
            <form action="/add" method="POST" enctype="multipart/form-data">
                <input name="n" class="input-field" placeholder="Product Name" required>
                <input name="c" class="input-field" placeholder="Product Code (e.g. KK-001)" required>
                <input name="p" class="input-field" placeholder="Price (Tk)" type="number" required>
                <textarea name="d" class="textarea-field" placeholder="Description..."></textarea>
                <label style="font-size:12px; font-weight:600;">Upload Gallery Image:</label>
                <input type="file" name="file" accept="image/*" style="margin-bottom:15px;" required>
                <button type="submit" style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:12px; font-weight:bold;">Publish Product</button>
            </form>
        </div>
        
        <h3>Inventory List</h3>
        {% for p in products %}
        <div style="background:#fff; padding:10px; border-radius:15px; margin-bottom:10px; display:flex; align-items:center; border:1px solid #eee;">
            <img src="{{ p['img'] }}" style="width:50px; height:50px; border-radius:10px; object-fit:cover; margin-right:15px;">
            <div style="flex-grow:1;"><b style="font-size:14px;">{{ p['name'] }}</b><br><small>Code: {{ p['code'] }}</small></div>
            <a href="/delete/{{ p['id'] }}" style="color:red; text-decoration:none; font-size:12px;">Delete</a>
        </div>
        {% endfor %}
    </div>
</body></html>
'''

# --- BACKEND LOGIC ---

@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string(HOME_HTML, products=products)

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string(ADMIN_HTML, products=products)

@app.route('/add', methods=['POST'])
def add():
    if session.get('admin'):
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_path = '/static/uploads/' + filename
            
            conn = get_db_connection()
            conn.execute('INSERT INTO products (name, price, img, code, desc) VALUES (?, ?, ?, ?, ?)', 
                         (request.form['n'], request.form['p'], img_path, request.form['c'], request.form['d']))
            conn.commit()
            conn.close()
    return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template_string('<body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;"><form method="POST" style="padding:40px;background:#fff;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.05);"><input name="u" placeholder="Admin"><br><input name="p" type="password" placeholder="Pass"><br><button>Login</button></form></body>')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('admin'):
        conn = get_db_connection()
        conn.execute('DELETE FROM products WHERE id = ?', (id,))
        conn.commit()
        conn.close()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

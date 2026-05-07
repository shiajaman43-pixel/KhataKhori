import os
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'arsvim_v1_gallery_secret')

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

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, price TEXT, img TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- CSS ---
CSS = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    :root { --primary: #111; --accent: #e63946; --gray: #f8f9fa; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; background: #fff; }
    .nav { position: sticky; top: 0; background: rgba(255,255,255,0.8); backdrop-filter: blur(15px); border-bottom: 1px solid #eee; z-index: 1000; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-weight: 800; font-size: 1.3rem; text-decoration: none; color: #000; }
    .container { max-width: 600px; margin: auto; padding: 20px; }
    .form-card { background: #fff; padding: 25px; border-radius: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .input-field { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 12px; border: 1px solid #ddd; font-family: inherit; }
    .file-input { margin-bottom: 20px; font-size: 14px; }
    .btn-submit { width: 100%; padding: 15px; background: #000; color: #fff; border: none; border-radius: 12px; font-weight: 800; cursor: pointer; }
    .admin-item { display: flex; align-items: center; background: #fff; padding: 12px; border-radius: 15px; margin-top: 10px; border: 1px solid #eee; }
    .admin-item img { width: 50px; height: 50px; border-radius: 10px; object-fit: cover; margin-right: 15px; }
</style>
'''

# --- ADMIN PANEL HTML ---
ADMIN_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">''' + CSS + '''</head>
<body style="background: var(--gray);">
    <nav class="nav"><span class="logo">ADMIN<span>PANEL</span></span><a href="/logout" style="text-decoration:none; color:red; font-weight:600;">Logout</a></nav>
    <div class="container">
        <div class="form-card">
            <h2 style="margin-top:0;">Upload Product</h2>
            <form action="/add" method="POST" enctype="multipart/form-data">
                <input name="n" class="input-field" placeholder="Product Name" required>
                <input name="p" class="input-field" placeholder="Price (Tk)" type="number" required>
                
                <label style="display:block; margin-bottom:8px; font-weight:600; font-size:14px;">Select from Gallery:</label>
                <input type="file" name="file" class="file-input" accept="image/*" required>
                
                <button type="submit" class="btn-submit">Publish to Store</button>
            </form>
        </div>

        <h3 style="margin-top:30px;">Inventory Management</h3>
        {% for p in products %}
        <div class="admin-item">
            <img src="{{ p['img'] }}">
            <div style="flex-grow:1;">
                <div style="font-weight:600; font-size:14px;">{{ p['name'] }}</div>
                <div style="font-size:12px; color:#888;">{{ p['price'] }} Tk</div>
            </div>
            <a href="/delete/{{ p['id'] }}" style="color:red; font-size:12px; text-decoration:none;" onclick="return confirm('Delete?')">Remove</a>
        </div>
        {% endfor %}
    </div>
</body></html>
'''

# --- ROUTES ---

@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template_string("... Home HTML Code ...", products=products) # Ager premium Home HTML ekhane bosiye din

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
        name = request.form['n']
        price = request.form['p']
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Render-er jonno path thik kora
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_path = '/static/uploads/' + filename
            
            conn = get_db_connection()
            conn.execute('INSERT INTO products (name, price, img) VALUES (?, ?, ?)', (name, price, img_path))
            conn.commit()
            conn.close()
    return redirect('/dashboard')

# Static file serving (Render-e chobi dekhanor jonno)
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['u'] == 'admin' and request.form['p'] == '12345':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template_string("... Login HTML ...")

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  

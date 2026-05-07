import os
from flask import Flask, render_template_string, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'arsvim_v1_upload_secret'

# --- UPLOAD CONFIG ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Folder na thakle toiri korbe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, img TEXT, stock INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

# --- ADMIN DASHBOARD (Updated with File Upload) ---
ADMIN_HTML = '''
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family: sans-serif; padding: 20px; background: #f4f4f4; }
    .upload-box { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
    input { display: block; width: 100%; margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
    button { background: #000; color: #fff; border: none; padding: 12px; width: 100%; border-radius: 8px; cursor: pointer; font-weight: bold; }
</style>
</head>
<body>
    <div class="upload-box">
        <h2>Add Product</h2>
        <form action="/add" method="POST" enctype="multipart/form-data">
            <input type="text" name="n" placeholder="Product Name" required>
            <input type="number" name="p" placeholder="Price (Tk)" required>
            <label style="font-size: 12px; color: #666;">Select Image from Gallery:</label>
            <input type="file" name="file" accept="image/*" required>
            <button type="submit">Upload & Publish</button>
        </form>
    </div>
    <br><a href="/">Back to Home</a>
</body></html>
'''

# --- ROUTES ---

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    items = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    # Home HTML-e {{ p[3] }} path-ti thakle auto chobi dekhabe
    return render_template_string("Home HTML code ekhane hobe...", products=items)

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect('/login')
    return render_template_string(ADMIN_HTML)

@app.route('/add', methods=['POST'])
def add():
    if session.get('admin'):
        name = request.form['n']
        price = request.form['p']
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Database-e relative path save hobe: /static/uploads/filename.jpg
            img_url = url_for('static', filename='uploads/' + filename)
            
            conn = sqlite3.connect('database.db')
            conn.execute('INSERT INTO products (name, price, img, stock) VALUES (?, ?, ?, 1)', 
                         (name, price, img_url))
            conn.commit()
            conn.close()
            
    return redirect('/dashboard')

# Static file server (Render-er jonno dorkar hote pare)
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
              

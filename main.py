import sqlite3
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_for_local')

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db()
        conn.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, img TEXT)''')
        conn.commit()
        conn.close()

init_db()

# --- HTML TEMPLATES ---
# (Age je HTML code gulo diyechi segulo ekhane thakbe)
# Sudhu Dashboard-e product delete korar option rakhte paren jate manage kora shohoj hoy.

@app.route('/')
def home():
    conn = get_db()
    items = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template_string(HOME_HTML, products=items) # HOME_HTML ager code theke niben

@app.route('/add_product', methods=['POST'])
def add_product():
    if session.get('logged_in'):
        name, price, img = request.form['p_name'], request.form['p_price'], request.form['p_img']
        conn = get_db()
        conn.execute('INSERT INTO products (name, price, img) VALUES (?, ?, ?)', (name, price, img))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

# ... Login/Logout logic ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  

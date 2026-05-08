from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "pixel_ultra_permanent_99"

# Database Setup (Permanent Storage)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50))

with app.app_context():
    db.create_all()

# --- CSS & Layout ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Press Start 2P', cursive; background: #fdfae6; padding: 20px; font-size: 10px; }
        .box { border: 4px solid #000; background: white; padding: 15px; margin-bottom: 20px; box-shadow: 6px 6px 0px #000; }
        .btn { font-family: 'Press Start 2P'; cursor: pointer; background: #ff4757; color: white; border: 3px solid #000; padding: 8px; font-size: 8px; text-decoration: none; display: inline-block; }
        input { font-family: 'Press Start 2P'; padding: 10px; border: 2px solid #000; margin: 5px 0; width: 85%; font-size: 8px; }
    </style>
</head>
<body>
    <div class="box" style="background:#2f3542; color:white; text-align:center;">PIXELULTRA SHOP</div>
    {{ content | safe }}
</body>
</html>
"""

@app.route('/')
def home():
    status = f"HI, {session['user_name']}" if 'user_id' in session else '<a href="/login" class="btn">LOGIN</a>'
    page_content = f"""
    <div class="box">
        {status} | <a href="/logout" class="btn" style="background:gray">LOGOUT</a>
        <hr>
        <h3>WELCOME TO THE SHOP</h3>
        <p>Products will appear here...</p>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, content=page_content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone, name, pwd = request.form['phone'], request.form['name'], request.form['password']
        if User.query.filter_by(phone=phone).first():
            return "Phone already exists! <a href='/register'>Try Again</a>"
        
        new_user = User(phone=phone, name=name, password=generate_password_hash(pwd))
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    
    reg_form = """
    <div class="box">
        <h3>REGISTER</h3>
        <form method="post">
            <input name="name" placeholder="Name" required><br>
            <input name="phone" placeholder="Phone" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit" class="btn">SIGN UP</button>
        </form>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, content=reg_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(phone=request.form['phone']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect('/')
        return "Invalid! <a href='/login'>Try Again</a>"
    
    login_form = """
    <div class="box">
        <h3>LOGIN</h3>
        <form method="post">
            <input name="phone" placeholder="Phone" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit" class="btn" style="background:#2ed573">ENTER</button>
        </form>
        <p>New? <a href="/register">Register</a></p>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, content=login_form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  

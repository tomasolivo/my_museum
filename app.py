from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from markupsafe import Markup
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts
                     (id INTEGER PRIMARY KEY, title TEXT, content TEXT, 
                     audio TEXT, timestamp TEXT)''')
        conn.commit()

init_db()

@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM posts ORDER BY timestamp DESC')
        posts = c.fetchall()
    return render_template('index.html', posts=posts, Markup=Markup)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        audio = request.form['audio']
        timestamp = request.form['timestamp'] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO posts (title, content, audio, timestamp) VALUES (?, ?, ?, ?)',
                      (title, content, audio, timestamp))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = c.fetchone()
    return render_template('post_detail.html', post=post, Markup=Markup)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = c.fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        audio = request.form['audio']
        timestamp = request.form['timestamp'] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE posts SET title = ?, content = ?, audio = ?, timestamp = ? WHERE id = ?',
                      (title, content, audio, timestamp, post_id))
            conn.commit()
        return redirect(url_for('index'))
    
    return render_template('edit_post.html', post=post, Markup=Markup)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'tomvs' and password == '802536':
            user = User(1)
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
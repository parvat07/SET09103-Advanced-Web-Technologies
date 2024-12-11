from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Retrieve the user from the database
    user = User.query.filter_by(username=session['username']).first()
    
    if user is None:
        return redirect(url_for('login'))  # Redirect if the user is not found

    # Retrieve tasks for the logged-in user
    tasks = Task.query.filter_by(user_id=user.id).all()
    return render_template('index.html', tasks=tasks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password')  # Flash message for invalid login
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        content = request.form['content']
        new_task = Task(content=content, user_id=user.id)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

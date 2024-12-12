from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.String(50), nullable=True)
    priority = db.Column(db.String(50), nullable=False, default='Low')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in or use a different email address.', 'danger')
            return redirect(url_for('register'))

        # If email doesn't exist, create the new user
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch tasks based on priority
    high_priority_tasks = Task.query.filter_by(user_id=current_user.id, priority='High').all()
    medium_priority_tasks = Task.query.filter_by(user_id=current_user.id, priority='Medium').all()
    low_priority_tasks = Task.query.filter_by(user_id=current_user.id, priority='Low').all()

    return render_template('dashboard.html', 
                           high_priority_tasks=high_priority_tasks,
                           medium_priority_tasks=medium_priority_tasks,
                           low_priority_tasks=low_priority_tasks)

@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form.get('title')  # This can now be None
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')
        user_id = current_user.id  # Replace with your logic to get the user ID

        # Create and save the task
        new_task = Task(
            title=title,  # Can be None
            description=description,
            due_date=due_date,
            priority=priority,
            user_id=user_id
        )
        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to task listing

    return render_template('create_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('Unauthorized action.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = request.form['due_date']
        task.priority = request.form['priority']

        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('edit_task.html', task = task)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Unauthorized action.')
        return redirect(url_for('dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('dashboard'))


@app.route('/task_detail/<int:task_id>')
@login_required
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('task_detail.html', task = task)

@app.route('/profile')
@login_required
def profile():

    return render_template('profile.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
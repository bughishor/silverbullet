from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_assets import Environment, Bundle
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql2375199:jJ9*yT6!@sql2.freesqldatabase.com/sql2375199'
app.config['SECRET_KEY'] = 'suchsecretverykey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('styles/styles.scss', filters='pyscss', output='all.css')
assets.register('scss_all', scss)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(200))
    last_login = db.Column(db.DateTime)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        login_time = datetime.now()

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        user.last_login = login_time
        db.session.commit()

        login_user(user, remember=True)
        return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        login_time = datetime.now()

        user = User.query.filter_by(username=username).first()

        if not name or not username or not password:
            flash('You must fill in all details')
            return redirect(url_for('register'))

        if user:
            flash('Email address already exists.')
            return redirect(url_for('register'))

        new_user = User(name=name, username=username, last_login=login_time,
                        password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)
        return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    logout_user()
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")

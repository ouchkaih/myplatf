from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username  # Add username to session
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('auth.login'))
    return render_template('connexion.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['passwordRepeat']
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('incription.html')

@auth.route('/')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return render_template('acceuil.html', username=user.username)
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('auth.login'))

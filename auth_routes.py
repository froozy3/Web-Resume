from app import app, db, login_manager
from models import User
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get('email')
        password = request.form.get("password")
        password2 = request.form.get("password2")

        existing_email = User.query.filter_by(
            email=email).first()  # обращаемся к бд за поиском email

        # обращаемся к бд за поиском password
        existing_user = User.query.filter_by(username=username).first()

        if password != password2:
            return render_template('register.html', error=("Password not confirm. Return again, please."))

        if existing_email:
            return render_template('register.html', error=(f"User with this email already exist!"))

        if existing_user:
            return render_template('register.html', error=(f"User with this username already exist!"))
        else:
            hashed_password = generate_password_hash(
                password, method="pbkdf2:sha256")
            user = User(username=username, email=email,
                        password=hashed_password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home_page'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')

        # Find user by username
        user = User.query.filter_by(username=username).first()

        # Check if user exists and the password is correct
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember_me == 'on')
            flash("Login successfull", 'success')
            return redirect(url_for('home_page'))

        return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

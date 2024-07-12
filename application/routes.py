from flask import render_template, request, redirect, url_for, flash, session
from main import app
from application.model import *

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 

        if not username or not password:
            flash('Please enter username and password')
            return redirect(url_for('login'))

        # if len(password) < 8:
        #     flash('Password must be at least 8 characters')
        #     return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        print(user, user.username, user.password)
        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        if password != user.password:
            flash('Invalid password')
            return redirect(url_for('login'))
        
        session['user'] = user.username
        session['role'] = user.roles[0].name

        flash('Login successful')
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        address = request.form['address']
        role = request.form['role']

        if not username or not password or not email or not role:
            flash('Please enter username, password, email and role')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        if role not in ['admin', 'store_manager', 'customer']:
            flash('Invalid role')
            return redirect(url_for('register'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists')
            return redirect(url_for('register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('register'))
        role = Role.query.filter_by(name=role).first()
        new_user = User(username=username, password=password, email=email, address=address, roles = [role])
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully')
        return redirect(url_for('login'))
from flask import render_template, request, redirect, url_for, flash, session
from main import app
from application.model import *
from datetime import datetime

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
    
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method =='GET':
        return render_template('add_category.html')
    
    if request.method == 'POST':
        name = request.form['category_name']
        description = request.form['description']

        if not name:
            flash('Please enter category name')
            return redirect(url_for('add_category'))
        
        if session['role'] == 'admin':
            category = Categories.query.filter_by(name=name).first()
            if category:
                flash('Category already exists')
                return redirect(url_for('add_category'))
            
            category = Categories(name=name, description=description)

            db.session.add(category)
            db.session.commit()
            flash('Category added successfully')
            return redirect(url_for('index'))
        
        elif session['role'] == 'store_manager':
            add_request = Requests.query.filter_by(request_type='add_category',new_category_name=name).first()
            if add_request:
                flash('Request already sent to admin for approval')
                return redirect(url_for('add_category'))
            
            category = Categories.query.filter_by(name=name).first()
            if category:
                flash('Category already exists')
                return redirect(url_for('add_category'))
            
            add_request = Requests(requester = session['user'],
                                   request_type = 'add_category',
                                   request_date = datetime.now(),
                                   new_category_name = name,
                                   new_category_description = description,
                                   request_status = 'pending')
            db.session.add(add_request)
            db.session.commit()
            flash('Request sent to admin for approval')
            return redirect(url_for('index'))
            
        else:
            flash('You are not authorized to add category')
            return redirect(url_for('index'))
        
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'GET':
        categories = Categories.query.all()
        return render_template('add_product.html', categories=categories)
    
    if request.method == 'POST':
        name = request.form['product_name']
        description = request.form['description']
        selling_price = request.form['selling_price']
        cost_price = request.form['cost_price']
        manufacturing_date = request.form['mfg_date']
        expiry_date = request.form['expiry_date']
        stock = request.form['quantity']
        category_id = request.form['category']

        manufacturing_date = datetime.strptime(manufacturing_date, '%Y-%m-%d')
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')

        if not name or not selling_price or not cost_price or not manufacturing_date or not expiry_date or not stock or not category_id:
            flash('Please enter all details')
            return redirect(url_for('add_product'))
        
        if session['role'] == 'store_manager':
            add_product = Products.query.filter_by(name=name).first()
            if add_product:
                flash('Product already exists')
                return redirect(url_for('add_product'))
            
            add_product = Products(name = name,
                                   description = description,
                                   selling_price = selling_price,
                                   cost_price = cost_price,
                                   manufacturing_date = manufacturing_date,
                                   expiry_date = expiry_date,
                                   stock = stock,
                                   category_id = category_id
                                   )
            db.session.add(add_product)
            db.session.commit()
            flash('Product added successfully')
            return redirect(url_for('index'))

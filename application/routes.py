from flask import render_template, request, redirect, url_for, flash, session
from main import app
from application.model import *
from datetime import datetime

@app.route('/')
def index():
    if 'user' in session:
        categories = Categories.query.all()
        return render_template('home.html', categories=categories)
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
        
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if session['role'] != 'store_manager':
        flash('You are not authorized to edit product')
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        product = Products.query.get(id)
        categories = Categories.query.all()
        if not product: 
            flash('Product not found')
            return redirect(url_for('index'))
        return render_template('edit_product.html',product = product, categories = categories)
    
    if request.method == 'POST':
        product = Products.query.get(id)
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

        if name:
            product.name = name
        if description:
            product.description = description
        if selling_price:
            product.selling_price = selling_price
        if cost_price:
            product.cost_price = cost_price
        if manufacturing_date:
            product.manufacturing_date = manufacturing_date
        if expiry_date:
            product.expiry_date = expiry_date
        if stock:
            product.stock = stock
        if category_id:
            product.category_id = category_id

        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('index'))
    
@app.route('/delete_product/<int:id>')
def delete_product(id):
    if session['role'] != 'store_manager':
        flash('You are not authorized to delete product')
        return redirect(url_for('index'))
    
    product = Products.query.get(id)
    if not product:
        flash('Product not found')
        return redirect(url_for('index'))
    
    db.session.delete(product)  
    db.session.commit()
    flash('Product deleted successfully')
    return redirect(url_for('index'))


@app.route('/add_cart/<int:id>', methods=['POST'])
def add_card(id):
    qty = request.form.get('quantity',None)

    try:
        qty = int(qty)
    except:
        flash('Invalid quantity')
        return redirect(url_for('index'))
    
    if 'user' not in session:
        flash('Please login to add product to cart')
        return redirect(url_for('login'))

    if 'role' in session and session['role'] != 'customer':
        flash('You are not authorized to add product to cart')
        return redirect(url_for('index'))
    
    product_details = Products.query.get(id)
    if not product_details:
        flash('Product not found')
        return redirect(url_for('index'))
    
    if not qty:
        flash('Please enter quantity')
        return redirect(url_for('index'))

    if product_details.stock < qty:
        flash('Stock not available')
        return redirect(url_for('index'))
    
    cart = Cart.query.filter_by(product_id=id, user=session['user']).first()
    if cart:
        cart.quantity += qty
    else:
        cart = Cart(product_id=id, user=session['user'], quantity=qty)
        db.session.add(cart)

    product_details.stock  = product_details.stock - qty
    db.session.commit()
    flash('Product added to cart')
    return redirect(url_for('index'))   


@app.route('/view_requests', methods=['GET', 'POST'])
def viewRequests():
    if request.method == 'GET':
        if 'role' in session and session['role'] == 'admin':
            requests = Requests.query.filter_by(request_status='pending').all()
            return render_template('requests.html',requests = requests)
       
        if 'role' in session and session['role'] == 'store_manager':
            requests = Requests.query.filter_by(requester=session['user']).all()
            return render_template('requests.html',requests = requests)

@app.route('/approve_request/<int:id>')
def approve_request(id):
    request = Requests.query.get(id)

    if request.request_type == 'add_category':
        category = Categories.query.filter_by(name=request.new_category_name).first()
        if category:
            request.request_status = 'rejected'
            db.session.commit()
            return redirect(url_for('viewRequests'))
        category = Categories(name=request.new_category_name, description=request.new_category_description)
        try:
            db.session.add(category)
            request.request_status = 'approved'
            db.session.commit()
            flash('Category added successfully')
            return redirect(url_for('viewRequests'))
        except:
            flash('Error approving request')
            return redirect(url_for('viewRequests'))

    if request.request_type == 'update_category':
        category = Categories.query.get(request.category_id)
        if not category:
            request.request_status = 'rejected'
            db.session.commit()
            return redirect(url_for('viewRequests'))
        category.name = request.new_category_name
        category.description = request.new_category_description
        request.request_status = 'approved'
        db.session.commit()
        flash('Category updated successfully')
        return redirect(url_for('viewRequests'))

    if request.request_type == 'delete_category':
        category = Categories.query.get(request.category_id)
        if not category:
            request.request_status = 'rejected'
            db.session.commit()
            return redirect(url_for('viewRequests'))
        db.session.delete(category)
        request.request_status = 'approved'
        db.session.commit()
        flash('Category deleted successfully')
        return redirect(url_for('viewRequests'))   


@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search = request.form.get('search',None)
        if not search:
            flash('Please enter search keyword')
            return redirect(url_for('index'))
        
        products = Products.query.filter(Products.name.like(f'%{search}%')).all()
        categories = Categories.query.filter(Categories.name.like(f'%{search}%')).all()
        return render_template('search.html',products=products,categories=categories)
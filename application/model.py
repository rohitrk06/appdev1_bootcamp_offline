from application.database import db

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=True)

    roles = db.relationship('Role', secondary='user_role')

    def __repr__(self):
        return f'<User {self.username}>'
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Role {self.name}>'
    
class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(80), db.ForeignKey('user.username'))
    role = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return f'<UserRole {self.id}>'
    
class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    products = db.relationship('Products', backref='categories', lazy=True)

    def __repr__(self):
        return f'<Categories {self.name}>' 

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    selling_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    manufacturing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    stock = db.Column(db.Integer, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __repr__(self):
        return f'<Products {self.name}>'
    
class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requester = db.Column(db.String(80), db.ForeignKey('user.username'))
    request_type = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable = True)
    request_date = db.Column(db.Date, nullable=False)
    new_category_name = db.Column(db.String(80), nullable=True)
    new_category_description = db.Column(db.String(255), nullable=True)
    request_status = db.Column(db.String(80), nullable=False)

    category = db.relationship('Categories', backref='requests', lazy=True)

    def __repr__(self):
        return f'<Requests: {self.request_type} _id_ {self.id}>'
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(80), db.ForeignKey('user.username'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Products', backref='cart', lazy=True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(80), db.ForeignKey('user.username'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    order_status = db.Column(db.String(80), nullable=False)

    product = db.relationship('Products', backref='orders', lazy=True)
    
    def __repr__(self):
        return f'<Orders: {self.id}>'
    


   
from flask import Flask, render_template, request, redirect, url_for, flash, session
from application.config import Config
from application.database import db
from application.model import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)   

    with app.app_context():
        db.create_all()

        if not Role.query.filter_by(name = 'admin').first():
            admin = Role(name='admin', description = 'Admin Role') 
            db.session.add(admin)
        if not Role.query.filter_by(name='store_manager').first():
            store_manager = Role(name='store_manager', description = 'Store Manager Role')
            db.session.add(store_manager)
        if not Role.query.filter_by(name='customer').first():
            customer = Role(name='customer', description = 'Customer Role')
            db.session.add(customer)

        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin',email='admin@gmail.com', address='StoreOwner', roles = [admin])
            db.session.add(admin_user)
        
        db.session.commit()

    return app

app = create_app()

from application.routes import *


if __name__ == '__main__':
    app.run(debug=True)
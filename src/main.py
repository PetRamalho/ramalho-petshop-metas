import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template
from flask_login import LoginManager # Added LoginManager
from src.models.user import db, User # Added User for user_loader
from src.routes.auth import auth_bp # Blueprint for authentication routes
from src.routes.main import main_bp # Blueprint for main application routes
from flask import redirect, url_for

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_very_secret_key_that_should_be_changed_in_production')

# Database Configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # The route for the login page (blueprint_name.view_function_name)
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth') # Changed from /api/auth to /auth to match login.html form action
app.register_blueprint(main_bp) # Register main blueprint without a prefix for routes like /dashboard

# Create database tables if they don't exist. 
# For production, use migrations (e.g., Flask-Migrate).
with app.app_context():
    # Ensure templates directory exists (though it should be created by now)
    if not os.path.exists(app.template_folder):
        os.makedirs(app.template_folder)
    db.create_all()
    
    # Criar usuários iniciais se não existirem
    if User.query.count() == 0:
        users_data = [
            {"username": "adm", "password": "adm123", "role": "master", "store_name": None},
            {"username": "alvarenga", "password": "alvarenga123", "role": "loja", "store_name": "Alvarenga"},
            {"username": "corbisier", "password": "corbisier321", "role": "loja", "store_name": "Corbisier"},
            {"username": "piraporinha", "password": "piraporinha321", "role": "loja", "store_name": "Piraporinha"}
        ]
        
        for user_data in users_data:
            new_user = User(username=user_data["username"], role=user_data["role"], store_name=user_data["store_name"])
            new_user.set_password(user_data["password"])
            db.session.add(new_user)
        
        db.session.commit()
        print("Usuários iniciais criados com sucesso!")

# The serve_static_or_index function was complex and might conflict with blueprint routes.
# Flask handles static files automatically if static_folder is set.
# Specific routes for pages like index will be handled by blueprints.

# A simple root route, main_bp will handle '/' and redirect to login or dashboard
@app.route('/')
def entry_point():
    return redirect(url_for('main.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


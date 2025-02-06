from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import User, db
from routes import register_routes

# Initialize Flask app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CSRF protection (default is True, so this line is optional)
app.config['WTF_CSRF_ENABLED'] = True

# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Set the login view

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register routes
register_routes(app)

# Create the database and tables
with app.app_context():
    db.create_all()

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
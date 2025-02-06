from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime  

# Initialize SQLAlchemy
db = SQLAlchemy()

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Explicitly set the table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) 
    code = db.Column(db.String(20), nullable=False) 
    directorate = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  # For admin approval
    is_active = db.Column(db.Boolean, default=True)    # For user activation status

    

    # Relationship to the Project table
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

# Project Model
class Project(db.Model):
    __tablename__ = 'project'  # Explicitly set the table name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    startdate = db.Column(db.Date, nullable=True)  # start date of the project
    duedate = db.Column(db.Date, nullable=True)  # Due date of the project   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Date the project was created
    budget = db.Column(db.Float, nullable=True, default=0.0)  # Budget for the project
    utilized = db.Column(db.Float, nullable=True, default=0.0)  # Utilized amount
    budgetus = db.Column(db.Float, nullable=True, default=0.0)  # Budget for the project
    utilizedus = db.Column(db.Float, nullable=True, default=0.0)  # Utilized amount
    remarks = db.Column(db.Text, nullable=True)  # Long text for remarks

    # Foreign key to the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Project {self.name} (User ID: {self.user_id})>'
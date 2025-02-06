from app import app, db , User
from werkzeug.security import generate_password_hash

# Create an application context
with app.app_context():
    # Create the admin user
    admin_username = 'admin'
    admin_password = 'admin$123'  # Change this to a secure password
    hashed_password = generate_password_hash(admin_password)

    # Check if the admin user already exists
    existing_admin = User.query.filter_by(username=admin_username).first()
    if existing_admin:
        print('Admin user already exists.')
    else:
        # Create the admin user
        admin_user = User(username=admin_username,email="admin@egyptair.com", code="0000", password=hashed_password,is_active=True, is_approved=True)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created successfully.')
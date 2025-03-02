from flask import render_template, redirect, url_for, flash, request , jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from models import User, Project, db
from forms import RegisterForm, LoginForm
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64 

def register_routes(app):

    @app.route('/', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            code = form.code.data
            password = form.password.data
            user = User.query.filter_by(code=code).first()

            if user and check_password_hash(user.password, password):
                if user.is_approved:
                    if user.is_active:
                        login_user(user)
                        flash('Logged in successfully!', 'success')
                        if user.username == 'admin':
                            return redirect(url_for('admin_index'))
                        else:
                            return redirect(url_for('projects'))
                    else:
                        flash('Your account has been deactivated. Please contact the admin.', 'warning')
                else:
                    flash('Your account is pending admin approval. Please wait.', 'warning')
            else:
                flash('Invalid username or password', 'danger')

        return render_template('login.html', form=form)
    
    

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            code = form.code.data 
            directorate = form.directorate.data
            password = form.password.data
            

            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('Username already taken. Please choose a different username.', 'danger')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)
            new_user = User(
            username=username,
            email=email, 
            code=code, 
            directorate=directorate,
            password=hashed_password,
            is_approved=False,
            is_active=True
        )

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please wait for admin approval.', 'success')
                return redirect(url_for('login'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('An error occurred during registration. Please try again.', 'danger')
                print(f"Database error: {e}")

        return render_template('register.html', form=form)

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin():
        if current_user.username != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('projects'))

        all_users = User.query.all()

        if request.method == 'POST':
            user_id = request.form.get('user_id')
            action = request.form.get('action')

            user = User.query.get(user_id)
            if user:
                if action == 'approve':
                    user.is_approved = True
                elif action == 'delete':
                    db.session.delete(user)
                elif action == 'deactivate':
                    user.is_active = False
                elif action == 'activate':
                    user.is_active = True

                try:
                    db.session.commit()
                    flash(f'User {user.username} has been {action}d.', 'success')
                except SQLAlchemyError as e:
                    db.session.rollback()
                    flash(f'An error occurred while processing your request.', 'danger')
                    print(f"Database error: {e}")

            return redirect(url_for('admin'))

        return render_template('admin.html', all_users=all_users)

    @app.route('/admin/index')
    @login_required
    def admin_index():
        # Ensure only the admin can access this page
        if current_user.username != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))

        # Fetch all users and group them by directorate
        #users = User.query.all()
        users = User.query.filter(User.username != 'admin').all()
        directorates = {}

        for user in users:
            if user.directorate not in directorates:
                directorates[user.directorate] = []
            directorates[user.directorate].append(user)

        return render_template('admin_index.html', directorates=directorates)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    
    @app.route('/projects')
    @login_required
    def projects():
        # Fetch the current user's projects
        user = current_user
        projects = Project.query.filter_by(user_id=user.id).all()

        return render_template('projects.html', user=user, projects=projects)

    @app.route('/projects/<int:user_id>')
    @login_required
    def admin_projects(user_id):
        # Ensure only the admin can access this page
        if current_user.username != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('login'))

        # Fetch the user and their projects
        user = User.query.get_or_404(user_id)
        projects = Project.query.filter_by(user_id=user.id).all()

        return render_template('projects.html', user=user, projects=projects)
       
    
    
    @app.route('/add_project', methods=['POST'])
    @login_required
    def add_project():
        data = request.get_json()
            
        new_project = Project(
            name=data['name'],
            description=data['description'],
            startdate=datetime.strptime(data['startdate'], '%Y-%m-%d').date(),  # Parse date string
            duedate=datetime.strptime(data['duedate'], '%Y-%m-%d').date(),  # Parse date string
            budget = data['budget'],
            utilized = data['utilized'],
            remarks=data['remarks'],
            user_id=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify(success=True)
    


# Route to fetch project details for editing
    @app.route('/get_project/<int:project_id>', methods=['GET'])
    @login_required
    def get_project(project_id):
        try:
            # Fetch the project from the database
            project = Project.query.get_or_404(project_id)

            # Ensure the current user owns the project
            if project.user_id != current_user.id:
                if current_user.username != 'admin':
                    return jsonify(success=False, message="You do not have permission to edit this project."), 403

            # Return the project details as JSON
            return jsonify({
                'success': True,
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'startdate': project.startdate.strftime('%Y-%m-%d'),  # Convert date to string
                    'duedate': project.duedate.strftime('%Y-%m-%d'),  # Convert date to string
                    'budget': project.budget,
                    'utilized': project.utilized,
                    'remarks': project.remarks
                }
            })
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500

    # Route to update a project
    @app.route('/edit_project/<int:project_id>', methods=['POST'])
    @login_required
    def edit_project(project_id):
        try:
            project = Project.query.get_or_404(project_id)

            if project.user_id != current_user.id:
                if current_user.username != 'admin':
                    return jsonify(success=False, message="You do not have permission to edit this project."), 403

            data = request.get_json()
            
            # Update project fields
            project.name = data['name'].strip()
            project.description = data['description'].strip()
            project.startdate = datetime.strptime(data['startdate'], '%Y-%m-%d').date() if data['startdate'] else None
            project.duedate = datetime.strptime(data['duedate'], '%Y-%m-%d').date() if data['duedate'] else None
            project.budget = float(data['budget']) if data['budget'] else 0.0
            project.utilized = float(data['utilized']) if data['utilized'] else 0.0
            project.remarks = data['remarks'].strip() if data['remarks'] else None

            db.session.commit()
            return jsonify(success=True, message="Project updated successfully!")
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=str(e)), 500

        
        
    @app.route('/delete_project/<int:project_id>', methods=['POST'])
    @login_required
    def delete_project(project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify(success=True)  # Return a JSON response
    
    @app.route('/delete_all_projects', methods=['POST'])
    @login_required
    def delete_all_projects():
        try:
            # Fetch all projects for the current user
            projects = Project.query.filter_by(user_id=current_user.id).all()

            # Delete all projects
            for project in projects:
                db.session.delete(project)

            # Commit the changes to the database
            db.session.commit()

            # Return a success response
            return jsonify(success=True, message="All projects deleted successfully!")
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            return jsonify(success=False, message=str(e)), 500
        
    @app.route('/admin/report')
    def admin_report():
        directorates = db.session.query(User.directorate).distinct().all()
        report_data = []

        for directorate in directorates:
            directorate = directorate[0]
            users = User.query.filter_by(directorate=directorate).all()
            total_budget = 0
            total_utilized = 0

            for user in users:
                projects = Project.query.filter_by(user_id=user.id).all()
                for project in projects:
                    total_budget += project.budget if project.budget else 0
                    total_utilized += project.utilized if project.utilized else 0

            if total_budget > 0:
                utilization_percentage = (total_utilized / total_budget) * 100
            else:
                utilization_percentage = 0

            # Skip entries with "Unknown Directorate" or None
            if directorate and directorate != "admin":
                report_data.append({
                    'directorate': directorate,
                    'total_budget': total_budget,
                    'total_utilized': total_utilized,
                    'utilization_percentage': utilization_percentage
                })

        # Round utilization_percentage to 2 decimal places
        for data in report_data:
            data['utilization_percentage'] = round(data['utilization_percentage'], 2)

        # Generate the graph
        img = io.BytesIO()
        plt.figure(figsize=(10, 6))
        plt.bar([data['directorate'] for data in report_data], [data['utilization_percentage'] for data in report_data])
        plt.xlabel('Directorate')
        plt.ylabel('Utilization Percentage')
        plt.title('Budget Utilization by Directorate')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()

        return render_template('admin_report.html', report_data=report_data, graph_url=graph_url)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email,ValidationError
import re

def validate_email(form, field):
    # Simple regex for email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, field.data):
        raise ValidationError('Invalid email address.') 
    
class RegisterForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=1, max=30)])
    email = StringField('Email', validators=[DataRequired(), validate_email]) 
    #email = StringField('Email') 
    code = StringField('الكود', validators=[DataRequired(), Length(min=1, max=10)])  
    directorate = StringField('الإدارة', validators=[DataRequired(), Length(min=1, max=40)])
    password = PasswordField('كلمة السر', validators=[DataRequired(), Length(min=1)])
    confirm_password = PasswordField('تأكيد كلمة السر', validators=[DataRequired(), EqualTo('password')])
     
    submit = SubmitField('تسجيل')

class LoginForm(FlaskForm):
    code = StringField('الكود', validators=[DataRequired(), Length(min=1, max=10)]) 
    password = PasswordField('كلمة السر', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('دخول')





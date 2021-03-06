from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo,  ValidationError
from simpleblog.models import User
from  flask_login import current_user



class RegistrationForm(FlaskForm):
    
    username = StringField('Username', 
                        validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email',
                            validators = [Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    picture = FileField("Update Profile Pic", validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sign Up')


    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("The username is already taken, Please check other")
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("The email is alraedy consumed, PLease insert other email")

class UpdateAccountForm(FlaskForm):

        
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators = [Email()])
    picture = FileField('Update profile picture', validators = [FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update")



    def validate_username(self, username):
        if username.data !=current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("Email already consumed, Please enter a new one")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError("The email has been already consumed ")



class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField("Remember me")
    
    
    submit = SubmitField("Login")

class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = TextAreaField('Content', validators = [DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError("No accounts with this email")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset Password')




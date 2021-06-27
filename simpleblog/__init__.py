
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail





app = Flask(__name__)

# configuration for protecting against cros site forgery attack
app.config['SECRET_KEY'] = '74fe2f906e292c6759f9d6535b80eb48' # for restricting the Cross site forgery
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = sys.argv[0]
app.config['MAIL_PASSWORD'] = sys.argv[1]
mail = Mail(app)

from simpleblog import routes
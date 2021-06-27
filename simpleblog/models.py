from simpleblog import db, app 
from datetime import datetime
from simpleblog import login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    # __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable =False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)
    post = db.relationship('Post', backref = 'author', lazy = True) # Post is the Post class here

    def get_reset_token(self, expires_time):
        s = Serializer(app.config['SECRET_KEY'], expires_time)
        return s.dumps({ 'user_id': self.id }).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = s.loads(token)['user_id']
        except:
            print("Nothing in the payload")
            return None
        return User.query.get(user_id) 

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    date_posted = db.Column(db.DateTime, nullable =  False, default = datetime.utcnow) # saving some default time
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False) #user is table name here
    def __repr__(self):
        return f"('{self.title}' , '{self.date_posted}')"


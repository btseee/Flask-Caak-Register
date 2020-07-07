from datetime import datetime
from flaskcaakregister import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    fname = db.Column(db.String(60), unique = False, nullable = False)
    lname = db.Column(db.String(60), unique = False, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    phone = db.Column(db.String(8), unique = True, nullable = False)
    isAdmin = db.Column(db.Boolean, default = False)
    image_file = db.Column(db.String(60), nullable = False, default='default.jpg')
    password = db.Column(db.String(60), nullable = False)
    tname = db.relationship('Team', backref = 'emp', lazy = True, uselist = False)
    absence = db.relationship('Absence', backref = 'abs', lazy = True, uselist = False)
    isApproved = db.Column(db.Boolean, default = False)
    status = db.Column(db.String(12), nullable = True, default = 'Тарсан')

    def __repr__(self):
        return f"User('{self.fname},{self.image_file},{self.email}')"

class Team(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    team_name = db.Column(db.String(100), nullable = True, default = 'Хоосон')
    start_time = db.Column(db.String(15), nullable = True)
    end_time = db.Column(db.String(15), nullable = True)
    total_hour = db.Column(db.String(15), nullable = True, default = '00:00')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logged_in = db.Column(db.String(15), nullable = True, default = 'None')
    logged_out = db.Column(db.String(15), nullable = True, default = 'None')
    logged_date = db.Column(db.String(15), nullable = True, default = 'None')

    def __repr__(self):
        return f"Team('{self.team_name},{self.total_hour},{self.start_time}')"

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    date = db.Column(db.DateTime, nullable = False, default = datetime.now())
    post = db.Column(db.Text, nullable = False, default = 'Хоосон')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    isAccepted = db.Column(db.Boolean, nullable = False, default = False)
    
    def __repr__(self):
        return f"Post('{self.post}, {self.date}')"
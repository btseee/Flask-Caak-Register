from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app=Flask(__name__)

#Secret key to secure the site
app.config['SECRET_KEY'] = 'dd555331221b5185ecb438cd64a8665f'
#database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
crypt = Bcrypt(app)
login_manager = LoginManager(app)
#passing a function name
login_manager.login_view = 'login'
#style for login page alert
login_manager.login_message_category = 'info'
login_manager.login_message = 'Энэ хуудасыг үзэхийн тулд эхлээд нэвтрэх шаардлагатай'

from flaskcaakregister import routes
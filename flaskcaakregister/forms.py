from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, TimeField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskcaakregister.models import User, Team, Absence
from flask_login import current_user
import string, datetime

class RegistrationForm(FlaskForm):
    fname = StringField('Нэр', validators=[DataRequired(), 
    Length(min = 2, max = 50, message = 'Хэрэглэгчийн нэр дор хаяж 2, хамгийн ихдээ 50 оронтой байх ёстой')])

    lname = StringField('Овог', validators=[DataRequired(), 
    Length(min = 2, max = 50, message = 'Хэрэглэгчийн нэр дор хаяж 2, хамгийн ихдээ 50 оронтой байх ёстой')])

    phone = StringField('Утасны дугаар', validators=[DataRequired(), 
    Length(min=8, max=8, message='Утасны дугаар буруу байна.')])

    email = StringField('Цахим шуудан', validators=[DataRequired(), Email()])

    password = PasswordField('Нууц үг', validators=[DataRequired(), 
    Length(min=8, max=25, message = 'Нууц үг дор хаяж 8, хамгийн ихдээ 25 оронтой байх ёстой')])

    confirm_password = PasswordField('Нууц үгээ баталгаажуулах', 
    validators=[DataRequired(), EqualTo('password', message='Нууц үг таарахгүй байна!')])

    submit = SubmitField('Илгээх')
    
    #checks if the email is already taken
    def validate_email(self, email):
        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('Энэ майл хаяг эзэнтэй байна!')
    #checks if the phone is valid
    def validate_phone(self, phone):
        if phone.data.isdigit():
            phone = User.query.filter_by(phone = phone.data).first()
            if phone:
                raise ValidationError('Энэ утасны дугаар аль хэдийн бүртгэгдсэн байна!')
        else:
            raise ValidationError('Утасны дугаар буруу байна!')
    
class LoginForm(FlaskForm):
    email = StringField('Майл хаяг', validators=[DataRequired(), 
    Email(message='Цахим шуудан буруу байна.')])
    password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=7, max=25)])
    remember = BooleanField('Намайг Сана')
    submit = SubmitField('Нэвтрэх')

class UpdateAccountForm(FlaskForm):
    email = StringField('Майл хаяг', validators=[DataRequired(), Email()])
    phone = StringField('Утасны дугаар')
    profile = FileField('Зургаа солих', validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Өөрчлөх')
    
    #checks if the phone is valid
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email = email.data).first()
            if email:
                raise ValidationError('Энэ майл хаяг эзэнтэй байна!')

class TeamForm(FlaskForm):
    team_name = SelectField('Ажиллах багийн нэр', validators=[DataRequired()], 
    choices=[('Хөгжүүлэлт', 'Хөгжүүлэлт'), ('Caak Орчуулага', 'Caak Орчуулага'), 
    ('Caak News Орчуулага', 'Caak News Орчуулага'), ('Видео','Видео'), ('График Дизайн','График Дизайн')])
    total_hour = TimeField('Нийт ажиллах цаг', format='%H:%M')
    start_time = TimeField('Эхлэх цаг', format='%H:%M')

class AdminRegisterForm(FlaskForm):
    fname = StringField('Нэр', validators=[DataRequired(), 
    Length(min = 2, max = 50, message = 'Хэрэглэгчийн нэр дор хаяж 2, хамгийн ихдээ 50 оронтой байх ёстой')])

    lname = StringField('Овог', validators=[DataRequired(), 
    Length(min = 2, max = 50, message = 'Хэрэглэгчийн нэр дор хаяж 2, хамгийн ихдээ 50 оронтой байх ёстой')])

    phone = StringField('Утасны дугаар', validators=[DataRequired(), 
    Length(min=8, max=8, message='Утасны дугаар буруу байна.')])

    email = StringField('Цахим шуудан', validators=[DataRequired(), Email(message='Цахим шуудан буруу байна.')])

    password = PasswordField('Нууц үг', validators=[DataRequired(), 
    Length(min=8, max=25, message = 'Нууц үг дор хаяж 8, хамгийн ихдээ 25 оронтой байх ёстой')])

    confirm_password = PasswordField('Нууц үгээ баталгаажуулах', 
    validators=[DataRequired(), EqualTo('password', message='Нууц үг таарахгүй байна!')])

    team_name = SelectField('Ажиллах багийн нэр', validators=[DataRequired()], 
    choices=[('Хөгжүүлэлт', 'Хөгжүүлэлт'), ('Caak Орчуулага', 'Caak Орчуулага'), 
    ('Caak News Орчуулага', 'Caak News Орчуулага'), ('Видео','Видео'), 
    ('График Дизайн','График Дизайн')])

    total_hour = TimeField('Нийт ажиллах цаг', format ='%H:%M', validators=[DataRequired()])

    start_time = TimeField('Эхлэх цаг', format='%H:%M',validators=[DataRequired()])
    
    submit = SubmitField('Нэмэх')
   
    def validate_email(self, email):
        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('Энэ майл хаяг эзэнтэй байна!')
    #checks if the phone is valid
    def validate_phone(self, phone):
        if phone.data.isdigit():
            phone = User.query.filter_by(phone = phone.data).first()
            if phone:
                raise ValidationError('Энэ утасны дугаар аль хэдийн бүртгэгдсэн байна!')
        else:
            raise ValidationError('Утасны дугаар буруу байна!')

class AbsenceForm(FlaskForm):
    post = TextAreaField('Чөлөө авах шалтгаан', validators=[DataRequired()])
    date = DateField('Хэзээ чөлөө авах', format='%Y-%m-%d')
    submit = SubmitField('Хүсэлт Илгээх')

    #checks if the phone is valid
    def validate_date(self, date):
        check = datetime.datetime.now()
        if date.data.month == check.month and date.data.year == check.year and date.data.day == check.month:
            raise ValidationError('Чөлөөг зөвхөн өмнөх өдөр авах боломжтой')
        elif date.data.month < check.month or date.data.day < check.day or date.data.year < check.year:
            raise ValidationError('Аль хэдийн өнгөрсөн өдөр чөлөө авч болохгүй')
            
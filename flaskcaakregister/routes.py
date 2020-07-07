from flask import render_template, request, session, logging, url_for, redirect, flash
from flaskcaakregister import app, db, crypt
from flaskcaakregister.models import User, Team, Absence
from flaskcaakregister.forms import RegistrationForm, LoginForm, UpdateAccountForm, TeamForm, AdminRegisterForm, AbsenceForm
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc
import secrets, os, datetime
from PIL import Image
from requests import get
from operator import add,sub
from datetime import datetime, timedelta, date, time
user_status = {
    'Ирсэн' : 'success',
    'Хоцорсон' : 'warning',
    'Чөлөөтэй' : 'muted',
    'Тасалсан' : 'danger',
}
#Ene function approve bolon admin register deer duudagddag.
#input ees ehnii 2 char bolon suulin 2 char iig int bolgoj bucaaj ogno
#huwisagchiin nernees n ymar ucirtai zuil boloh n hargadana.
def time(input):
    hour = input[0:2]
    minute = input[-2:]
    return int(hour), int(minute)

#Cag duusah hugatsaag toocooloh function
def end_time_calc(start_time, time, minute):
    s_time = datetime.strptime(start_time, "%H:%M")
    d_time = timedelta(hours = time)
    d_minute = timedelta(minutes= minute)
    return s_time + d_time + d_minute

#burtguuleh heseg. Hereglegch ooriin medeellee hangasni daraa
#admin ruu haygiig idvhjuuleh huselt ywuulah bogood
#admin ajillah cag bolon yamr bagt ajillah uguig n hiij ogsni daraa haygiig idhvjuulne
@app.route("/register", methods=['POST', 'GET'])
def register():
    # Login in hiitsn bj register luu oroh ged baiwal bucaagad home page ruu ywuulna
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm() 
    # herew buglsun form batalgaajuulsan bol daraahiiig unshinaa
    if form.validate_on_submit():
        hashed_password = crypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(phone=form.phone.data, fname=form.fname.data, 
        lname=form.lname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        team_link = Team(user_id = user.id)
        db.session.add(team_link)
        db.session.commit()
        flash(f'{form.fname.data} хаяг амжилттай бүртгэгдэж, админ руу илгээлээ.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form, title='Бүртгүүлэх')

#login heseg - ehleed password bolon email hayag database deer
#baigaa uguig shalgasanii daraa admin nevterch baina uu
#eswel jiriin hereglegch newterch baina uu gdgiig shalgana
@app.route('/', methods=['POST', 'GET'])
@app.route("/login", methods=['POST', 'GET'])
def login():
    #allowed Ip address
    work_ip = '66.181.166.147'
    form = LoginForm()
    ip = get('https://api.ipify.org').text
    dtime=datetime.now().strftime('%H:%M')
    ddate=datetime.today().strftime('%Y-%m-%d')
    # checks if the user is already logged in or not
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        #checks if the current ip is same as the work ip
        if ip != work_ip:
            user = User.query.filter_by(email = form.email.data).first()
            if user and crypt.check_password_hash(user.password, form.password.data):
                log_in = datetime.now().strftime("%H:%M")
                if user.isApproved:
                    login_user(user, remember=form.remember.data)
                    if current_user.isAdmin==0:
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                        flash('Зөвхөн ажлын WIFI аар нэвтэрсэнээр цаг бүртгэх болно болно','danger')
                else:
                    flash('Хаяг хараахан зөвшөөрөгдөөгүй байна.', 'danger')   
            else:
                flash('Нууц үг эсвэл майл хаяг буруу байна', 'danger')  
        else:
            user = User.query.filter_by(email = form.email.data).first()
            if user and crypt.check_password_hash(user.password, form.password.data):
                log_in = datetime.now().strftime("%H:%M")
                if user.isApproved:
                    login_user(user, remember=form.remember.data)
                    user.status = 'Ирсэн'
                    if current_user.isAdmin==0:
                        login_approved=Team(logged_in=dtime, user_id=user.id, logged_date=ddate, start_time= user.tname.start_time,total_hour=user.tname.total_hour, end_time=user.tname.end_time)
                        db.session.add(login_approved)
                        db.session.commit()
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                        flash('Зөвхөн ажлын WIFI аар нэвтэрсэнээр цаг бүртгэх болно болно','danger')
                else:
                    flash('Хаяг хараахан зөвшөөрөгдөөгүй байна.', 'danger')   
            else:
                flash('Нууц үг эсвэл майл хаяг буруу байна', 'danger')       
    return render_template("index.html", form = form, title='Нэвтрэх')


#Nuur heseg end hereglegch ooriin cagiin huwaari
#busad gishuudiin irsen baigaa uguig shalgana
@app.route("/home_section", methods=['POST', 'GET'])
@login_required
def home():
    #user_status in dictionary bogood hamgiin deed hesegt baigaa
    #Onoodr heden bolon heddeh we gdgiig haruulah zorilgotoi cag
    dtime = datetime.now()
    ddate=date.today()
    acc_status = user_status.get(current_user.status)
    day_off = Absence.query.filter_by(isAccepted = False).all() 
    if current_user.isAdmin:
        #ymr hereglgech orj baigaag haruulah gej
        user_list = User.query.filter_by(isApproved = True).filter_by(isAdmin=0).all()
        #shine hayag neelgeh huselt
        new_req = len(User.query.filter_by(isApproved = False).all())
        return render_template('home.html', title='Нүүр хуудас', user_list = user_list, dtime = dtime, request = new_req, 
        acc_status = acc_status, day_off = day_off)
    else:
        #listend oruulah 
        starttime= [st[0] for st in Team.query.filter(current_user.id==Team.user_id).with_entities(Team.start_time)]
        endtime= [et[0] for et in Team.query.filter(current_user.id==Team.user_id).with_entities(Team.end_time)]
        loggedin= [li[0] for li in Team.query.filter(current_user.id==Team.user_id).with_entities(Team.logged_in)]
        loggedout= [lo[0] for lo in Team.query.filter(current_user.id==Team.user_id).with_entities(Team.logged_out)]
        
        #DATAnd none gsn ugugdliig 00:00 bolgoj orluulah 
        for n, i in enumerate(loggedout):
            if i == 'None':
                loggedout[n] = "00:00"

        #iluu tsag hotsorson tsag zzarlah 
        undertime = [] 
        overtime=[]

        #DAVTALTAAR ylgavar avah 
        for i in range(0, len(starttime)): 
            #ali neg ni ih bagaar ni jishihgui bol -1 day nemegdeed ih muuhai garch bsn bolno 
            if datetime.strptime(str(loggedout[i]), '%H:%M') >= datetime.strptime(str(endtime[i]), '%H:%M'):
                overtime.append(str(datetime.strptime(str(loggedout[i]), '%H:%M') - datetime.strptime(str(endtime[i]), '%H:%M')))
            else:
                overtime.append(str(datetime.strptime(str(endtime[i]), '%H:%M') - datetime.strptime(str(loggedout[i]), '%H:%M')))
            #======================================================================================================================
            if datetime.strptime(str(loggedin[i]), '%H:%M') >= datetime.strptime(str(starttime[i]), '%H:%M'):
                undertime.append(str(datetime.strptime(str(loggedin[i]), '%H:%M') - datetime.strptime(str(starttime[i]), '%H:%M')))
            else:
                undertime.append(str(datetime.strptime(str(starttime[i]), '%H:%M') - datetime.strptime(str(loggedin[i]), '%H:%M')))
        
        return render_template('home.html', title='Нүүр хуудас',len= len(undertime), undertime=undertime, overtime=overtime,Team = Team.query.join(User).filter(current_user.id==Team.user_id).all() , dtime = dtime, ddate=ddate)

# logs out the user
@app.route("/logout")
def logout():
    work_ip = '66.181.166.147'
    ip = get('https://api.ipify.org').text

    if current_user.isAdmin:
        current_user.status="Тарсан"
        db.session.commit()
        logout_user()
        return redirect(url_for("login"))

    else:
        if work_ip != ip:
            logout_user()
            return redirect(url_for("login"))
        else:
            dtime=datetime.now().strftime('%H:%M')
            endtime=Team.query.filter(current_user.status=="Ирсэн").filter(Team.logged_out=="None").update(dict(logged_out=dtime))
            db.session.commit()
            current_user.status="Тарсан"
            db.session.commit()
            logout_user()
            flash('Амжилттай бүртгэлээ', 'info')
            return redirect(url_for("login"))

#zurgiin nerig ooorchilj, hemjeeg n jijg blgno
def save_pic(form_profile):
    #profile zurgiin ner davhtsaj magdgu ucir random usg too
    #nemj ner hiilee
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_profile.filename)
    #zurgiin ner
    picture_fn = random_hex + f_ext
    #zurg haana hadgalagdah location
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    #Tupple for image size
    output_size = (175, 175)
    #zurgiin hemjeeg bagasgah
    i = Image.open(form_profile)
    i.resize((output_size), Image.ANTIALIAS)
    i.save(picture_path)
    return picture_fn

#Hereglegch profile hayag
#Zurag ner email hayg zergee solij bolno.
@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    new_req = len(User.query.filter_by(isApproved = False).all())
    form = UpdateAccountForm()
    if form.validate_on_submit():
        #Herew user profile zurgaa solison bol daraah kodig unshina
        if form.profile.data:
            old_picture = current_user.image_file
            #hereglegchees awch bui profile data
            picture_file = save_pic(form.profile.data)
            current_user.image_file = picture_file
            #database deer huucin baigaa zurgnuudig hadgalah shaardlaggui uchir ustgana
            #oorchilsn thohioldold shuud huucni zurgig ustgana
            if old_picture != 'default.jpg':
                os.remove(os.path.join(app.root_path, 'static/img', old_picture))
        #shine ner, email hayag solih heseg
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Хаягын мэдээллийг өөрчилсөн', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    img_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('account.html', title='Profile', img_file = img_file, form = form, request = new_req)

@app.route("/admin/new_account/approve", methods=['POST', 'GET'])
@login_required
def approve():
    #Admin nevtreh erhte heseg
    #ene function odohono ajilaggagui
    if current_user.isAdmin:
        users = User.query.filter_by(isApproved = False).all()
        new_req = len(User.query.filter_by(isApproved = False).all())
        form = TeamForm()
        #heden shirheg shine hayg neeh huselt baigaagaar n function davtagdana.
        if request.method == 'POST':
            if request.form['submit'] == 'no':
                team = Team.query.filter(Team.user_id == users[0].id).first()
                db.session.delete(users[0])
                db.session.delete(team)
                db.session.commit()
                flash('Хаягыг устгалаа','danger')
                return redirect(url_for('approve'))
            if request.form['submit'] == 'yes':
                #Database deer huulahaas omno string orgollttei bolgj baina.
                string_start_time = form.start_time.data.strftime("%H:%M")
                string_total_hour = form.total_hour.data.strftime("%H:%M")
                #string_total_hour aas cag bolon minutig integer herlbreer bucaaj ogno
                hour, minute = time(string_total_hour)
                #end timiig oor function deer bodood return hiisn n
                end_time = end_time_calc(string_start_time, hour, minute)
                users[0].tname.end_time = end_time.strftime("%H:%M")
                users[0].tname.start_time = string_start_time
                users[0].tname.total_hour = string_total_hour
                users[0].isApproved = True
                db.session.commit()
                flash('Хаяг зөвшөөрөгдөж, идэвхжлээ', 'success')
                return redirect(url_for('approve'))
                
        return render_template('request.html', form = form, users = users, request = new_req)
    else:
        flash('Админ зөвхөн нэвтэрч болно.', 'danger')
        return redirect(url_for('login'))

@app.route("/admin/add_worker", methods=['POST', 'GET'])
@login_required
def admin_register():
    if current_user.isAdmin:
        form = AdminRegisterForm()
        new_req = len(User.query.filter_by(isApproved = False).all())
        if form.validate_on_submit():
            hashed_password = crypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(phone=form.phone.data, 
            fname=form.fname.data, lname=form.lname.data,
            email=form.email.data, password=hashed_password, isApproved = True)
            db.session.add(user)
            db.session.commit()
            #dongoj say databased hiigdsen useree phone - oor n filterdeed awna
            added_user = User.query.filter_by(phone = form.phone.data).first()
            string_start_time = form.start_time.data.strftime("%H:%M")
            string_total_hour = form.total_hour.data.strftime("%H:%M")
            hour, minute = time(string_total_hour)
            end_time = end_time_calc(string_start_time, hour, minute)
            string_end_time = end_time.strftime("%H:%M")
            team = Team(team_name = form.team_name.data, end_time = string_end_time, total_hour = string_total_hour, user_id = user.id, start_time = string_start_time)
            db.session.add(team)
            db.session.commit()
            flash(f'{form.fname.data} Хаяг амжилттай нээгдлээ.', 'success')
            return redirect(url_for('admin_register'))
    else:
        flash('Энэ хуудасыг үзэх эрх байхгүй байна.', 'danger')
        return redirect(url_for('home'))
    
    return render_template("admin_register.html", form=form, title='Шинэ ажилтан бүртгүүлэх', request = new_req)

@app.route('/profile/<int:id>', methods = ['GET', 'POST'])
@login_required
def visit_profile(id):
    if current_user.isAdmin:
        new_req = len(User.query.filter_by(isApproved = False).all())
        user = User.query.filter_by(id = id).first()
        if user:
            return render_template("profile.html", user = user, request = new_req)
        else:
            flash('Хэрэглэгч олдсонгүй', 'danger')
            return redirect(url_for('home'))

    flash('Бусад хэрэглэгчийн мэдээллийг зөвхөн админ үзэх боломжтой', 'danger')
    return redirect(url_for('home'))

@app.route('/absence', methods = ['GET', 'POST'])
def absence():
    form = AbsenceForm()
    new_req = len(User.query.filter_by(isApproved = False).all())
    if form.validate_on_submit():
        req = Absence(post = form.post.data, user_id = current_user.id, date = form.date.data)
        db.session.add(req)
        db.session.commit()
        flash('Чөлөө авах хүсэлт админд илгээгдлээ.', 'success')
        return redirect(url_for('home'))

    return render_template("absence.html", form = form, title = 'Чөлөө авах', request = new_req)
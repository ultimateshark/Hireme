from flask import Flask,render_template,session,flash,redirect,url_for
from models import db
from flask_migrate import Migrate
from flask_mail import Mail,Message
from datetime import datetime,timedelta
from passlib.hash import sha256_crypt
import uuid
import random
import string
#creating object of FLask as app
app=Flask(__name__)

#configurations for database
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:mom0511@localhost/Hireme"# setting of database uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)#initializing the database with the app
db.app=app#assign the app to the db app

#configurations for sending email
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='ultimateshark.in@gmail.com'
app.config['MAIL_PASSWORD']='***********'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)


#initializing app for migration
migrate = Migrate(app, db)

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		try:
			if session["logged_in"]:
				return f(*args, **kwargs)
			else:
				return redirect("/login")
		except:
			return redirect("/login")
	return wrap


#get the object of seeker data model
def GetSeekerInfo():
	current_user=session["username"]
	data=Job_seeker.query.filter_by(email=current_user).first()
	return data


#get the object of recruiter data model
def GetRecruitejerInfo():
	current_user=session["username"]
	data=Recruiter.query.filter_by(email=current_user).first()
	return data

def pass_generator(size=8, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def get_token():
	token=""
	while True:
		token=pass_generator()
		x=Verification.query.filter_by(token=token).all()
		if len(x)==0:
			break
	return token




#route to home
@app.route("/")
def Home():
    return render_template("home.html")


@app.route("/verify/<string:token>")
def Verify(token):
    try:
        check=Verification.query.filter_by(token=token).first()
        if check.for_recruiter:
            rec=Recruiter.query.filter_by(recruiter_id=check.user_id).first()
            rec.verified=True
        else:
            seeker=Job_seeker.query.filter_by(seeker_id=check.user_id).first()
            seeker.verified=True
        db.session.delete(check)
        db.session.commit()
        flash("Account Successfully Verified!!!")
        return redirect(url_for("Login"))
    except:
        flash("Something Went Wrong!!!")
        return redirect(url_for("Home"))



@app.route("/login-seeker")
def Login_Seeker():
	try:
		if request.method=="POST":
			email=request.form['email']
			passwd=request.form['passwd']
			user=Job_seeker.query.filter_by(email=email).all()
			if len(user)==0:
				user=Job_seeker(email=email,passwd=passwd)
				db.session.add(user)
				token=get_token()
				check=Verification(token=token,for_recruiter=False,user_id=user.recruiter_id)
				db.session.add(check)
				msg=Message('From Hireme',sender='ultimateshark.in@gmail.com',recipients=[email])
				msg.body="Please Click on the link to verify your account at Hireme\n: "+"http://127.0.0.1:5000/verify/"+token
				mail.send(msg)
				db.session.commit()
				flash("Account Created Please Check Your Email For Verification Link")
				return redirect(url_for("Login_Seeker"))
			user=user[0]
			if not user.verified:
				flash("Please Verify Your Email To Login")
				return redirect(url_for("Login_Seeker"))
			if sha256_crypt.verify(user.passwd,passwd):
				session['logged_in']=True
				session['username']=user.email
				flash("Login Successfull")
				return render_template("Dashboard_seeker.html")
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))



@app.route("/login-recruiter")
def Login_Recruiter():
	try:
		if request.method=="POST":
			email=request.form['email']
			passwd=request.form['passwd']
			user=Recruiter.query.filter_by(email=email).all()
			if len(user)==0:
				user=Recruiter(email=email,passwd=passwd)
				db.session.add(user)
				token=get_token()
				check=Verification(token=token,for_recruiter=True,user_id=user.recruiter_id)
				db.session.add(check)
				msg=Message('From Hireme',sender='ultimateshark.in@gmail.com',recipients=[email])
				msg.body="Please Click on the link to verify your account at Hireme\n: "+"http://127.0.0.1:5000/verify/"+token
				mail.send(msg)
				db.session.commit()
				flash("Please Check Your Email For Verification Link")
				return redirect(url_for("Login_Recruiter"))
			user=user[0]
			if not user.verified:
				flash("Please Verify Your Email To Login")
				return redirect(url_for("Login_Recruiter"))
			if sha256_crypt.verify(user.passwd,passwd):
				session['logged_in']=True
				session['username']=user.email
				flash("Login Successfull")
				return render_template("Dashboard_recruiter.html")
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/job-list")
def Job_List():
	try:
		user=GetSeekerInfo()
		intrests=user.interested_stack.split(" ")
		result=[]
		for inst in intrests:
			list_val=Job_posts.query.filter(Job_posts.skills.like(inst)).order_by(Job_posts.date_posted.desc()).all()
			result.append(list_val)
		return render_template('all_jobs.html')
	except Exception as e:
		raise

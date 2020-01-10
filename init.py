from flask import Flask,render_template,session,flash,redirect,url_for,request
from models import *
from flask_migrate import Migrate
from flask_mail import Mail,Message
from datetime import datetime,timedelta
from passlib.hash import sha256_crypt
from functools import wraps
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
def GetRecruiterInfo():
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

@app.route("/loginpage/<string:user_type>")
def Login_Page(user_type):
	try:
		return render_template('login.html',user_type=user_type)
	except Exception as e:
		flash('Something Went Wrong')
		return redirect(url_for("Home"))

@app.route("/add-education-page/<string:user_type>")
@login_required
def Add_Education_Page(user_type):
	try:
		return render_template('education_details.html',user_type=user_type)
	except Exception as e:
		flash('Something Went Wrong')
		return redirect(url_for("Home"))

@app.route("/add-education/<string:user_type>",methods=["GET","POST"])
@login_required
def Add_Education(user_type):
	try:
		if request.method=="POST":
			user=None
			if user_type=="seeker":
				user=GetSeekerInfo()
			elif user_type=="recruiter":
				user=GetRecruiterInfo()
			school=request.form['school']
			level=request.form['level']
			percentage=request.form['percentage']
			from_date=request.form['from_date']
			to_date=request.form['to_date']
			edu=Education_details(school_name=school,education_level=level,percentage=percentage,from_date=from_date,to_date=to_date)
			db.session.add(edu)
			user.education_det.append(edu)
			db.session.commit()
			flash('Education Details Added Successfully')
			return redirect("/add-education-page/"+user_type)
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route("/add-employment-page/<string:user_type>")
@login_required
def Add_Employment_Page(user_type):
	try:
		return render_template('employment_details.html',user_type=user_type)
	except Exception as e:
		flash('Something Went Wrong')
		return redirect(url_for("Home"))

@app.route("/add-employment/<string:user_type>",methods=["GET","POST"])
@login_required
def Add_Employment(user_type):
	try:
		if request.method=="POST":
			user=None
			if user_type=="seeker":
				user=GetSeekerInfo()
			elif user_type=="recruiter":
				user=GetRecruiterInfo()
			company_name=request.form['company_name']
			role=request.form['role']
			description=request.form['description']
			from_date=request.form['from_date']
			to_date=request.form['to_date']
			emp=Employment_details(company_name=company_name,role=role,description=description,from_date=from_date,to_date=to_date)
			db.session.add(emp)
			user.employment_det.append(emp)
			db.session.commit()
			flash('Employment Details Added Successfully')
			return redirect("/add-employment-page/"+user_type)
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route("/add-jobpost-page")
@login_required
def Add_Jobpost_Page():
	try:
		return render_template('job_post.html')
	except Exception as e:
		flash('Something Went Wrong')
		return redirect(url_for("Home"))

@app.route("/add-jobpost",methods=["GET","POST"])
@login_required
def Add_Jobpost():
	try:
		if request.method=="POST":
			user=GetRecruiterInfo()
			role=request.form['role']
			locations=request.form['locations']
			min_exp=request.form['min_exp']
			max_exp=request.form['max_exp']
			salary_from=request.form['salary_from']
			salary_upto=request.form['salary_upto']
			description=request.form['description']
			skills=request.form['skills']
			perks=request.form['perks']
			post=Job_posts(role=role,loactions=loactions,description=description,salary_range_from=salary_from,salary_range_to=salary_upto,skills=skills,perks=perks,date_posted=datetime.now())
			db.session.add(post)
			user.job_posts.append(emp)
			db.session.commit()
			flash('Post Added Successfully')
			return redirect("/add-employment-page/"+user_type)
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/posted-jobs")
@login_required
def Posted_Jobs():
	try:
		user=GetRecruiterInfo()
		all_posts=user.job_posts
		return render_template('posted_jobs.html',all_posts=all_posts)
	except Exception as e:
		flash('Something Went Wrong')
		return redirect(url_for("Home"))


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



@app.route("/login-seeker",methods=["GET","POST"])
def Login_Seeker():
	try:
		if request.method=="POST":
			email=request.form['email']
			passwd=request.form['passwd']
			user=Job_seeker.query.filter_by(email=email).all()
			if len(user)==0:
				user=Job_seeker(email=email,passwd=sha256_crypt.encrypt(passwd))
				db.session.add(user)
				token=get_token()
				check=Verification(token=token,for_recruiter=False,user_id=user.seeker_id)
				db.session.add(check)
				msg=Message('From Hireme',sender='ultimateshark.in@gmail.com',recipients=[email])
				msg.body="Please Click on the link to verify your account at Hireme\n: "+"http://127.0.0.1:5000/verify/"+token
				# mail.send(msg)
				db.session.commit()
				flash("Account Created Please Check Your Email For Verification Link")
				return redirect(url_for("Login_Seeker"))
			user=user[0]
			if not user.verified:
				flash("Please Verify Your Email To Login")
				return redirect('/loginpage/seeker')
			if sha256_crypt.verify(passwd,user.passwd):
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



@app.route("/login-recruiter",methods=["GET","POST"])
def Login_Recruiter():
	try:
		if request.method=="POST":
			email=request.form['email']
			passwd=request.form['passwd']
			user=Recruiter.query.filter_by(email=email).all()
			if len(user)==0:
				user=Recruiter(email=email,passwd=sha256_crypt.encrypt(passwd))
				db.session.add(user)
				token=get_token()
				check=Verification(token=token,for_recruiter=True,user_id=user.recruiter_id)
				db.session.add(check)
				msg=Message('From Hireme',sender='ultimateshark.in@gmail.com',recipients=[email])
				msg.body="Please Click on the link to verify your account at Hireme\n: "+"http://127.0.0.1:5000/verify/"+token
				# mail.send(msg)
				db.session.commit()
				flash("Please Check Your Email For Verification Link")
				return redirect(url_for("Login_Recruiter"))
			user=user[0]
			if not user.verified:
				flash("Please Verify Your Email To Login")
				return redirect('/loginpage/recruiter')
			if sha256_crypt.verify(passwd,user.passwd):
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
@login_required
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
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/job-list/<string:key>")
def Job_List_Search(key):
	try:
		result=[]
		list_val=Job_posts.query.filter(Job_posts.skills.like(key)).order_by(Job_posts.date_posted.desc()).all()
		result.append(list_val)
		return render_template('all_jobs.html')
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route("/applied-jobs")
@login_required
def Applied_To():
	try:
		user=GetSeekerInfo()
		applied=user.applied_to
		return render_template('all_jobs.html',applied_to=applied)
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/apply-to-<int:job_id>",methods=["GET","POST"])
@login_required
def Apply_To_Job(job_id):
	try:
		if request.method=="POST":
			user=GetSeekerInfo()
			new_application=Relation_Jobpost_Jobseeker(cover_letter=request.form['cover_letter'],date_applied=datetime.now())
			db.session.add(new_application)
			user.applied_to.append(new_application)
			job=Job_posts.query.filter_by(post_id=job_id).first()
			job.applications.append(new_application)
			db.session.commit()
			flash("Application Sent!!!")
			return redirect(url_for('Job_List'))
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


app.secret_key="lalalalalalala12121212121212121218585"

if __name__ == '__main__':
	app.run(debug=True)

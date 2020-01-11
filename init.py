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
app.config['MAIL_PASSWORD']='********'
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
				flash('Please Login First')
				return redirect("/")
		except:
			flash('Something Went Wrong')
			return redirect("/")
	return wrap

def condidate_login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		try:
			if session["logged_in"] and session['type']=='seeker':
				if CheckSeekerUpdate():
					flash('Please Update Your Profile First!!!')
					return render_template('update_seeker.html')
				return f(*args, **kwargs)
			elif session["logged_in"] and not session['type']=='seeker':
				flash('Please Login As Candidate')
				return redirect('/')
			else:
				flash('Please Login First')
				return redirect("/")
		except:
			flash('Something Went Wrong')
			return redirect("/")
	return wrap


def recruiter_login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		try:
			if session["logged_in"] and session['type']=='recruiter':
				if CheckRecruiterUpdate():
					flash('Please Update Your Profile First!!!')
					return render_template('update_recruiter.html')
				return f(*args, **kwargs)
			elif session["logged_in"] and not session['type']=='recruiter':
				flash('Please Login As Recruiter')
				return redirect('/')
			else:
				flash('Please Login First')
				return redirect("/")
		except:
			flash('Something Went Wrong')
			return redirect("/")
	return wrap


def CheckSeekerUpdate():
	try:
		current_user=session["username"]
		data=Job_seeker.query.filter_by(email=current_user).first()
		if not data.updated:
			return True
		else:
			return False
	except Exception as e:
		return False

def CheckRecruiterUpdate():
	try:
		current_user=session["username"]
		data=Recruiter.query.filter_by(email=current_user).first()
		if not data.updated:
			return True
		else:
			return False
	except Exception as e:
		return False

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

def pass_generator(size=15, chars=string.ascii_uppercase + string.digits):
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
	try:
		if session["logged_in"]:
			return redirect('/dashboard')
		else:
			posts=Job_posts.query.order_by(Job_posts.date_posted.desc()).limit(20).all()
			return render_template("home.html",posts=posts)
	except:
		posts=Job_posts.query.order_by(Job_posts.date_posted.desc()).limit(20).all()
		return render_template("home.html",posts=posts)

@app.route('/dashboard')
def Dashboard():
	try:
		if session['type']=='seeker':
			posts=Job_posts.query.order_by(Job_posts.date_posted.desc()).limit(20).all()
			return render_template('seeker_dash.html',posts=posts)
		elif session['type']=='recruiter':
			posts=GetRecruiterInfo().job_posts
			return render_template('recruiter_dash.html',posts=posts)
	except:
		posts=Job_posts.query.order_by(Job_posts.date_posted.desc()).limit(20).all()
		return render_template("home.html",posts=posts)

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
@recruiter_login_required
def Add_Jobpost_Page():
	try:
		return render_template('job_post.html')
	except Exception as e:
		flash('Something Went Wrong')
		return redirect(url_for("Home"))

@app.route("/add-jobpost",methods=["GET","POST"])
@recruiter_login_required
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
			post=Job_posts(role=role,locations=locations,min_experience=min_exp,max_experience=max_exp,description=description,salary_range_from=salary_from,salary_range_to=salary_upto,skills=skills,perks=perks,date_posted=datetime.now())
			db.session.add(post)
			user.job_posts.append(post)
			filename = 'application'+str(post.post_id)+'.jpg'
			imageData=request.files['pfile'].read()
			with open('/home/ubuntu/Hireme/Hireme/static/img/'+filename, 'wb') as f:
				f.write(imageData)
			db.session.commit()
			flash('Post Added Successfully')
			return redirect(url_for("Add_Jobpost_Page"))
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/posted-jobs")
@recruiter_login_required
def Posted_Jobs():
	try:
		user=GetRecruiterInfo()
		all_posts=user.job_posts
		return render_template('job_list.html',posts=all_posts)
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
        return redirect('/dashboard')
    except:
        flash("Something Went Wrong!!!")
        return redirect(url_for("Home"))



@app.route("/login-seeker",methods=["GET","POST"])
def Login_Seeker():
	try:
		try:
			if session['logged_in']:
				return redirect('/dashboard')
		except:
			pass
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
				msg.body="Please Click on the link to verify your account at Hireme\n: "+"http://18.188.232.204/verify/"+token
				mail.send(msg)
				db.session.commit()
				flash("Check Your Email For Verification Link")
				return redirect('/loginpage/recruiter')
			user=user[0]
			if not user.verified:
				flash("Please Verify Your Email To Login")
				return redirect('/loginpage/seeker')
			if sha256_crypt.verify(passwd,user.passwd):
				session['logged_in']=True
				session['username']=user.email
				session['type']='seeker'
				flash("Login Successfull")
				return redirect('/dashboard')
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))



@app.route("/login-recruiter",methods=["GET","POST"])
def Login_Recruiter():
	try:
		try:
			if session['logged_in']:
				return redirect('/dashboard')
		except:
			pass
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
				msg.body="Please Click on the link to verify your account at Hireme\n: "+"http://18.188.232.204/verify/"+token
				mail.send(msg)
				db.session.commit()
				flash("Please Check Your Email For Verification Link")
				return redirect('/loginpage/recruiter')
			user=user[0]
			if not user.verified:
				flash("Please Verify Your Email To Login")
				return redirect('/loginpage/recruiter')
			if sha256_crypt.verify(passwd,user.passwd):
				session['logged_in']=True
				session['username']=user.email
				session['type']='recruiter'
				posts=user.job_posts
				flash("Login Successfull")
				return redirect('/dashboard')
		else:
			flash("Invalid Request")
			return redirect(url_for("Home"))
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route('/update-profile/recruiter',methods=['GET','POST'])
def Update_Profile_Recruiter():
	try:
		if request.method=="POST":
			user=GetRecruiterInfo()
			name=request.form['name']
			company_name=request.form['company_name']
			role=request.form['role']
			user.name=name
			user.current_company=company_name
			user.role=role
			user.updated=True
			filename = 'recruiter'+str(user.recruiter_id)+'.jpg'
			imageData=request.files['pfile'].read()
			with open('/home/ubuntu/Hireme/Hireme/static/img/'+filename, 'wb') as f:
				f.write(imageData)
			db.session.commit()
			flash('Profile Updated Successfully')
			return redirect('/dashboard')
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route('/update-profile/seeker',methods=['GET','POST'])
def Update_Profile_Seeker():
	try:
		if request.method=="POST":
			user=GetSeekerInfo()
			name=request.form['name']
			company_name=request.form['company_name']
			role=request.form['role']
			interested_stack=request.form['interested_stack']
			current_package=request.form['current_package']
			user.name=name
			user.current_company=company_name
			user.role=role
			user.interested_stack=interested_stack
			user.current_package=current_package
			user.updated=True
			filename = 'seeker'+str(user.seeker_id)+'.jpg'
			imageData=request.files['pfile'].read()
			with open('/home/ubuntu/Hireme/Hireme/static/img/'+filename, 'wb') as f:
				f.write(imageData)
			db.session.commit()
			flash('Profile Updated Successfully')
			return redirect('/dashboard')
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route('/get-candidate-details/<int:c_id>/<int:job_id>')
def Get_Candidate_Details(c_id,job_id):
	try:
		rel=Relation_Jobpost_Jobseeker.query.filter_by(jobpost_id=job_id,seeker_id=c_id).first()
		if not rel.for_post.recruiter.recruiter_id==GetRecruiterInfo().recruiter_id:
			flash("Not Authorized!!!")
			return redirect('/dashboard')
		if rel.status==0:
			rel.status=1
		seeker=rel.seeker
		db.session.commit()
		return render_template('app_prof.html',rel=rel,seeker=seeker)
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route('/accept-application/<int:app_id>')
def Accept_Application(app_id):
	try:
		rel=Relation_Jobpost_Jobseeker.query.filter_by(application_id=app_id).first()
		if not rel.for_post.recruiter.recruiter_id==GetRecruiterInfo().recruiter_id:
			flash("Not Authorized!!!")
			return redirect('/dashboard')
		rel.status=2
		seeker=rel.seeker
		db.session.commit()
		return render_template('app_prof.html',rel=rel,seeker=seeker)
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route('/reject-application/<int:app_id>')
def Reject_Application(app_id):
	try:
		rel=Relation_Jobpost_Jobseeker.query.filter_by(application_id=app_id).first()
		if not rel.for_post.recruiter.recruiter_id==GetRecruiterInfo().recruiter_id:
			flash("Not Authorized!!!")
			return redirect('/dashboard')
		rel.status=3
		seeker=rel.seeker
		db.session.commit()
		return render_template('app_prof.html',rel=rel,seeker=seeker)
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))





@app.route('/job-list-all')
def Job_List_All():
	try:
		posts=Job_posts.query.all()
		return render_template('job_list.html',posts=posts,heading="All Job Posts")
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/job-list")
@condidate_login_required
def Job_List():
	try:
		user=GetSeekerInfo()
		if user.interested_stack==None:
			flash('You do not have any interest mentioned, Please Update')
			return redirect('/')
		intrests=user.interested_stack.split(" ")
		result=[]
		for inst in intrests:
			list_val=Job_posts.query.filter(Job_posts.skills.like('%'+inst+'%') | Job_posts.role.like('%'+inst+'%')).order_by(Job_posts.date_posted.desc()).all()
			result+=list_val
		return render_template('job_list.html',posts=result,heading="My Job Chart")
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/job-list-search",methods=['GET','POST'])
def Job_List_Search():
	try:
		key=request.form['key']
		result=[]
		list_val=Job_posts.query.filter(Job_posts.skills.like('%'+key+'%') | Job_posts.role.like('%'+key+'%') | Job_posts.locations.like('%'+key+'%') ).order_by(Job_posts.date_posted.desc()).all()
		result+=list_val
		return render_template('job_list.html',posts=result,heading="Searched Jobs")
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route("/applied-jobs")
@condidate_login_required
def Applied_To():
	try:
		user=GetSeekerInfo()
		applied=user.applied_to
		return render_template('applied_jobs.html',posts=applied)
	except:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/apply-to-page/<int:job_id>")
@login_required
def Apply_To_Job_page(job_id):
	try:
		try:
			user=GetSeekerInfo()
			check=Relation_Jobpost_Jobseeker.query.filter_by(seeker_id=user.seeker_id,jobpost_id=job_id).all()
			if len(check)>0:
				flash('Already Applied')
				return redirect('/get-job-details/'+str(job_id))
			return render_template('application_form.html',job_id=job_id)
		except:
			flash('Please Login First')
			return redirect('/')
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route("/apply-to-<int:job_id>",methods=["GET","POST"])
@condidate_login_required
def Apply_To_Job(job_id):
	try:
		if request.method=="POST":
			user=GetSeekerInfo()
			check=Relation_Jobpost_Jobseeker.query.filter_by(seeker_id=user.seeker_id,jobpost_id=job_id).all()
			if len(check)>0:
				flash('Already Applied')
				return redirect('/get-job-details/'+str(job_id))
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


@app.route("/get-job-details/<int:job_id>")
def Get_Job_Details(job_id):
	try:
		user=None
		try:
			user=session['type']
		except Exception as e:
			pass
		details=Job_posts.query.filter_by(post_id=job_id).first()
		posts=Job_posts.query.filter(Job_posts.role.like(details.role)).limit(15).all()
		return render_template('job_detail.html',post=details,posts=posts,user=user)
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route("/applications/<int:job_id>")
@recruiter_login_required
def Application(job_id):
	try:
		user=GetRecruiterInfo()
		details=Job_posts.query.filter_by(post_id=job_id).first()
		if not user.recruiter_id==details.recruiter_id:
			flash('You Are Not Authorized')
			return redirect('/get-job-details/'+str(job_id))
		apps=details.applications
		return render_template('view_applications.html',applications=apps,heading='View Applications')
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))

@app.route('/view-profile-page')
@login_required
def View_Profile_Page():
	try:
		user=None
		if session['type']=='seeker':
			user=GetSeekerInfo()
			return render_template('view_prof_seeker.html',user=user)
		else:
			user=GetRecruiterInfo()
			return render_template('view_prof_recruiter.html',user=user)
	except Exception as e:
		flash("Something Went Wrong!!!")
		return redirect(url_for("Home"))


@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
	try:
		user=session['username']
		session.pop('username',None)
		session.pop('type',None)
		session['logged_in']=False
		flash("Successfully Logged Out.")
		return redirect(url_for('Home'))
	except:
		flash("ALREADY LOGGED OUT")
		return redirect("/login")

app.secret_key="lalalalalalala12121212121212121218585"

if __name__ == '__main__':
	app.run(debug=True)

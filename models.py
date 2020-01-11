from flask_sqlalchemy import SQLAlchemy

#createing SQLAlchemy object as db
db=SQLAlchemy()

#model for recruiter table which inherits the properties of Model from SQLAlchemy
class Recruiter(db.Model):
    __tablename__="recruiter" #name of table
    recruiter_id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True,nullable=False)
    passwd=db.Column(db.String(200),nullable=False)
    verified=db.Column(db.Boolean,default=False) #to check if user email is verified or not
    updated=db.Column(db.Boolean,default=False)
    current_company=db.Column(db.String(200))
    role=db.Column(db.String(200))
    name=db.Column(db.String(50))
    employment_det=db.relationship('Employment_details',cascade="all,delete",backref=db.backref("recruiter")) # one to many relation with Employment table
    education_det=db.relationship('Education_details',cascade="all,delete",backref=db.backref("recruiter")) # one to many relationship with Education details table
    job_posts=db.relationship('Job_posts',cascade="all,delete",backref=db.backref("recruiter")) # one to many relation with Job Posts table


#model for Job Seekers details table
class Job_seeker(db.Model):
    __tablename__="job_seeker" #name of table
    seeker_id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),unique=True,nullable=False)
    passwd=db.Column(db.String(200),nullable=False)
    verified=db.Column(db.Boolean,default=False) #to check if user email is verified or not
    updated=db.Column(db.Boolean,default=False)
    interested_stack=db.Column(db.String(200))
    current_company=db.Column(db.String(200))
    current_package=db.Column(db.String(200))
    role=db.Column(db.String(200))
    name=db.Column(db.String(50))
    employment_det=db.relationship('Employment_details',cascade="all,delete",backref=db.backref("seeker")) # one to many relation with Employment table
    education_det=db.relationship('Education_details',cascade="all,delete",backref=db.backref("seeker")) # one to many relationship with Education details table
    applied_to=db.relationship("Relation_Jobpost_Jobseeker",cascade="all,delete",backref=db.backref("seeker"))# many to many relation with job posts table



#model for Employment details table
class Employment_details(db.Model):
    __tablename__="employment_details"
    employment_id=db.Column(db.Integer,primary_key=True)
    company_name=db.Column(db.String(200),nullable=False)
    role=db.Column(db.String(200),nullable=False)
    from_date=db.Column(db.DateTime)
    to_date=db.Column(db.DateTime)
    description=db.Column(db.String(1000),nullable=True)
    recruiter_id=db.Column(db.Integer,db.ForeignKey("recruiter.recruiter_id"))# to store id of the recruiter in case of recruiters details
    seeker_id=db.Column(db.Integer,db.ForeignKey("job_seeker.seeker_id"))# to store id of the seeker in case of seeker details


#model for Education details table
class Education_details(db.Model):
    __tablename__="education_details"
    education_id=db.Column(db.Integer,primary_key=True)
    school_name=db.Column(db.String(200),nullable=False)
    education_level=db.Column(db.String(200),nullable=False)
    percentage=db.Column(db.Float,nullable=False)
    from_date=db.Column(db.DateTime,nullable=False)
    to_date=db.Column(db.DateTime,nullable=False)
    recruiter_id=db.Column(db.Integer,db.ForeignKey("recruiter.recruiter_id"))# to store id of the recruiter in case of recruiters details
    seeker_id=db.Column(db.Integer,db.ForeignKey("job_seeker.seeker_id"))# to store id of the seeker in case of seeker details


#model for job posts table
class Job_posts(db.Model):
    __tablename__="job_posts"
    post_id=db.Column(db.Integer,primary_key=True)
    recruiter_id=db.Column(db.Integer,db.ForeignKey("recruiter.recruiter_id"))
    role=db.Column(db.String(200),nullable=False)
    locations=db.Column(db.String(200),default="Not Specified")
    min_experience=db.Column(db.Integer,default=0) #minimum experience required for the post
    max_experience=db.Column(db.Integer) #maximum experience required for the post
    salary_range_from=db.Column(db.Float)
    salary_range_to=db.Column(db.Float)
    description=db.Column(db.String(2000),nullable=False)
    skills=db.Column(db.String(2000),nullable=False)
    perks=db.Column(db.String(2000))
    date_posted=db.Column(db.DateTime)




#Intermediate table to establish many to many relationship of job seekers and job posts they have applied to
class Relation_Jobpost_Jobseeker(db.Model):
    __tablename__="relation_jobpost_jobseeker"
    application_id=db.Column(db.Integer,primary_key=True)
    status=db.Column(db.Integer,default=0)# 0 for applied/sent 1 for Viewed , 2 for Accepted and 3 for Rejected
    cover_letter=db.Column(db.String(1000),nullable=True)
    date_applied=db.Column(db.DateTime)
    seeker_id=db.Column(db.Integer,db.ForeignKey("job_seeker.seeker_id"))
    jobpost_id=db.Column(db.Integer,db.ForeignKey("job_posts.post_id"))
    for_post=db.relationship("Job_posts",cascade="all,delete",backref=db.backref("applications"))


#model to store tokken for Verification
class Verification(db.Model):
    token_id=db.Column(db.Integer,primary_key=True)
    token=db.Column(db.String(200),nullable=False)
    for_recruiter=db.Column(db.Boolean,nullable=False)#Flase for seeker and true for recruiter
    user_id=db.Column(db.Integer,unique=True,nullable=False)

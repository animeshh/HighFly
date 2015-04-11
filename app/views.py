from flask import Flask, redirect, url_for, session, request, jsonify,render_template
from flask_oauthlib.client import OAuth
from app import app,db
from models import User,Resume
import json,urllib,datetime
import HTMLParser
from collections import defaultdict
import urllib2
from xml.dom import minidom
from glassdoor import get

app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)
#75ovm95gewyled
#VZwnHKUuyCXNX0to
linkedin = oauth.remote_app(
    'linkedin',
    consumer_key='75ovm95gewyled',
    consumer_secret='VZwnHKUuyCXNX0to',
    request_token_params={
        'scope': 'r_basicprofile,r_fullprofile,r_emailaddress,r_contactinfo,r_network',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)



@app.route('/')
def index():
    if 'linkedin_token' in session:
        me = linkedin.get('people/~:(first-name,last-name,headline,picture-url,public-profile-url,formatted-name,summary,skills,email-address,main-address,phone-numbers,industry)')
        # user=User(nickname="ahsan",email="sc@n.com")
        # db.session.add(user)
        # db.session.commit()
        # return jsonify(me.data)
        u=User(me.data['formattedName'],me.data['emailAddress'])

        flag=u.signUp()
        print '-------------------------------'
        print me.data['industry']
        
        if flag == 1:
            first_resume={}
            first_resume['firstName']=me.data['firstName']
            first_resume['lastName']=me.data['lastName'],
            first_resume['skills']=me.data['skills']
            first_resume['emailAddress']=me.data['emailAddress']

            # first_resume['address']=me.data['mainAddress']

            jso = json.dumps(first_resume)

            r=Resume(title='first linkedin resume',json_data=jso,creator=u)
            db.session.add(r)
            db.session.commit()
        num=u.getId()
        print(u.id)
        session['user_id']=(num)
        return render_template("index.html",
        title = 'Home',
        user = me)
        # return jsonify(me.data)

    return render_template("login.html")

@app.route('/test')
def test():
    return jsonify(session)
@app.route('/resumes')
def show_resume():
    user=User.query.filter_by(id=session['user_id']).first()
    resumes=user.resumes.all()
    # return jsonify(resumes)
    return render_template("resume_list.html",
        title = 'Resumes',
        resumes = resumes,user=user)

@app.route('/resume/add', methods=['GET', 'POST'])
def add_resume():
    if request.method == 'POST':
        title=title=request.form['title']
        json_data=request.form["skill_json"]
        created_time=datetime.datetime.utcnow()
        edited_time=datetime.datetime.utcnow()
        user=User.query.filter_by(id=session['user_id']).first()


        r=Resume(title=title,json_data=json_data,created_time=created_time,edited_time=edited_time,creator=user)
        db.session.add(r)
        db.session.commit()

        return redirect(url_for('show_resume'))
    user=User.query.filter_by(id=session['user_id']).first()

    return render_template("add_resume.html",
        title = 'Add Resume',
        user=user)

@app.route('/resume/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        title=title=request.form['title']
        json_data=request.form["skill_json"]
        created_time=datetime.datetime.utcnow()
        edited_time=datetime.datetime.utcnow()
        user=User.query.filter_by(id=session['user_id']).first()


        r=Resume(title=title,json_data=json_data,created_time=created_time,edited_time=edited_time,creator=user)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('show_resume'))
    #Animesh,code added for auto fill form
    alldata = pdftoTxt()
    userdata = dataFilter(alldata[0])
    return render_template("upload_resume.html",title = 'Upload Resume',user=userdata)

def dataFilter(alldata):
    import re
    userdata = {}
    #index = re.match("\bContact\b",alldata,re.IGNORECASE).start()
    #print index
    #print alldata
    data = alldata.split()
    pattern1 = re.compile("email",re.IGNORECASE) 
    pattern2 = re.compile("mobile|phone",re.IGNORECASE)
    pattern3 = re.compile("no|info|:|-",re.IGNORECASE)
    flag1 = False
    flag2 = False
    for index,value in enumerate(data):
        if pattern1.match(value):
            if data[index+1]==':' or data[index+1]=='-':
                userdata['email'] = data[index+2]
            else:
                userdata['email'] = data[index+1]
            flag1 = True
        if pattern2.match(value):
            if pattern3.match(data[index+1]):
                userdata['contact'] = data[index+2]
            else:
                userdata['contact'] = data[index+1]
            flag2 = True
        if flag1 and flag2:
            break
    userdata['firstName'] = data[0]
    userdata['lastName'] =  data[1]
    
    return userdata

def pdftoTxt():
    import pyPdf
    from PyPDF2 import PdfFileReader, PdfFileWriter
    pdf = PdfFileReader(open("animesh_resume.pdf", "rb"))
    sentences = []
    #parse pdf into text
    for page in pdf.pages:
        sentences.append(page.extractText())
        #print page.extractText()
        return sentences
@app.route('/resume/<int:resume_id>', methods=['GET', 'POST'])
@app.route('/resume/edit/<int:resume_id>', methods=['GET', 'POST'])
def editResume(resume_id):
    if request.method == 'POST':
        resume=Resume.query.filter_by(id=resume_id).first()
        resume.title=request.form['title']
        resume.json_data=request.form["skill_json"]
        resume.edited_time=datetime.datetime.utcnow()
        db.session.commit()

        return redirect(url_for('show_resume'))
    user=User.query.filter_by(id=session['user_id']).first()
    resume=Resume.query.filter_by(id=resume_id).first()
    form_data=json.loads(resume.json_data)
    skills=form_data['skills']['values']

    h = HTMLParser.HTMLParser()
    skill_list=json.JSONEncoder().encode(form_data['skills']['values'])
    # skill_list=str(skill_list)
    skill_list=skill_list.replace("u","")
    skill_list=h.unescape(skill_list)
    print(skill_list)
    return render_template("edit_resume.html",
        title = 'Edit Resume',
        form_data=form_data,
        skill_list=skill_list,
        resume_id=resume_id,
        user=user,r_title=resume.title)

@app.route('/resume/delete/<int:resume_id>')
def delete_resume(resume_id):
    pass

@app.route('/connections')
def show_connections():
	user=User.query.filter_by(id=session['user_id']).first()
	if 'linkedin_token' in session:
		conns = linkedin.get('people/~/connections:(headline,id,first-name,last-name,location,industry,picture-url)')

	f = open('data.json', 'w')
	f.write(json.dumps(conns.data, indent=1))
	f.close()
	connections = json.loads(json.dumps(conns.data, indent=1))
    # Get an id for a connection. We'll just pick the first one.
	print len(connections['values'])
	index = 0
	all = list()
	categorized = defaultdict(list)
	countdata = defaultdict()
    
	for conn in connections['values']:
		try:
            #all.append()
			name = conn['firstName'].encode("utf-8")+' '+conn['lastName'].encode("utf-8")
			industry = conn['industry'].encode("utf-8")
			headline = conn['headline'].encode("utf-8")
			contact = (name, industry, headline)
            #conn['firstName'].encode("utf-8"), conn['lastName'].encode("utf-8"), conn['id'].encode("utf-8"), , conn['picture-url'].encode("utf-8"), conn['location'].encode("utf-8")
			all.append(contact)
			categorized[industry].append(contact)
		except KeyError: pass
		index = index+1

	for key in categorized:
		if len(categorized[key])*1000/index > 10 :
			countdata[key] = len(categorized[key])
			print key,countdata[key]
	return render_template("connections.html", title = 'Connections', all_conn=all, cat_conn=categorized, cat_count = countdata, user=user)

'''	
@app.route('/connections')
def show_connections():
	user=User.query.filter_by(id=session['user_id']).first()
	categorized = list()
	conns = list()
	return render_template("connections.html", title = 'Connections', all_conn=conns, cat_conn=categorized, user=user)
'''
	
@app.route('/jobs')
def show_jobs():
    user=User.query.filter_by(id=session['user_id']).first()
    if 'linkedin_token' in session:
        jobs = linkedin.get('https://api.linkedin.com/v1/job-search:(jobs:(id,customer-job-code,active,posting-date,expiration-date,posting-timestamp,expiration-timestamp,company:(id,name),position:(title,location,job-functions,industries,job-type,experience-level),skills-and-experience,description-snippet,description,salary,job-poster:(id,first-name,last-name,headline),referral-bonus,site-job-url,location-description))?distance=10&job-title=product&facets=company,location&facet=industry,6&facet=company,1288&sort=DA')
	
	#f = open('jobs.json', 'w')
    #f.write(json.dumps(jobs.data, indent=1))
    #f.close()
	resume=user.resumes.first()
	
	skill_json=json.loads(resume.json_data)
	skill_length=len(skill_json['skills']['values'])
	skill_list=list()
	total_job_list=list()
	if skill_length>2 :
		for x in range(0, 2):
			skill_name=skill_json['skills']['values'][x]['skill']['name']
			url = 'http://service.dice.com/api/rest/jobsearch/v1/simple.json?skill='+skill_name
			response = urllib2.urlopen(url).read()
			f = open('jobs_'+skill_name+'.json', 'w')
			f.write(json.dumps(response, indent=1))
			f.close()
			job_list = list()
			jobs_data = json.loads(response)
			for job in jobs_data['resultItemList']:
				job_post=(job['detailUrl'], job['jobTitle'], job['company'], job['location'], job['date'])
				job_list.append(job_post)
			main_job_node=(skill_name,job_list)
			total_job_list.append(main_job_node)
    return render_template("jobs.html",
        title = 'Jobs', all_jobs=total_job_list, user=user)
		
@app.route('/jobs/details', methods=['GET', 'POST'])
def job_details():

	user=User.query.filter_by(id=session['user_id']).first()
	if request.method == 'GET':
		url=request.args.get('joburl')
		company=request.args.get('company')
		
		x = get('dropbox')
		print x
		
		
		job_response = urllib2.urlopen(url).read()
		p = LinksParser()
		p.feed(job_response)
		p.close()
		url = 'http://access.alchemyapi.com/calls/text/TextGetRankedConcepts'
		apikey = '6e2ca8f176761b589a9bee72a3ff6ed8703e0706' #your API key goes here
		params = urllib.urlencode({
			'apikey': apikey,
			'text': p.data,
			'showSourceText': '0', #shows the original text sent to the API
		})
			
		alchemyThis = urllib2.urlopen(url, params).read()
		xmldoc = minidom.parseString(alchemyThis)
		nodes = xmldoc.getElementsByTagName('concept')
		all = list()
		for node in nodes:
			textVal = node.getElementsByTagName('text')[0]
			rel = node.getElementsByTagName('relevance')[0]
			dbpedia = node.getElementsByTagName('dbpedia')[0]
			concept = (textVal.childNodes[0].data, rel.childNodes[0].data, dbpedia.childNodes[0].data)
			all.append(concept)
			
		
		#print job_response
		
	return render_template("job_details.html", title = "Job Analysis", job_des = p.data, concepts = all, user=user)
	
@app.route('/login')
def login():
    return linkedin.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('linkedin_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')


def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query

class LinksParser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.recording = 0
    self.data = []

  def handle_starttag(self, tag, attributes):
    if tag != 'div':
      return
    if self.recording:
      self.recording += 1
      return
    for name, value in attributes:
      if name == 'id' and value == 'detailDescription':
        break
    else:
      return
    self.recording = 1

  def handle_endtag(self, tag):
    if tag == 'div' and self.recording:
      self.recording -= 1

  def handle_data(self, data):
    if self.recording:
      self.data.append(data)
	  
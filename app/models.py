from app import db
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64))
	email = db.Column(db.String(120), index=True, unique=True)
	resumes=db.relationship('Resume',backref='creator',lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.nickname)

	def __init__(self, nickname, email):
		self.nickname = nickname
		self.email=email

	def signUp(self):
		u=User.query.filter_by(email=self.email).first()
		flag=0
		if u is None:
			db.session.add(self)
			db.session.commit()
			flag=1
		us=User.query.filter_by(email=self.email).first()
		self.id=us.id
		return flag


	def getId(self):
		return self.id

class Resume(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(400))
	json_data = db.Column(db.Text)
	created_time = db.Column(db.DateTime)
	edited_time = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Resume %r>' % (self.title)

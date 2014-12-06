import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/highfly_db'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
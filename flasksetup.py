#from flask import Flask
#app = Flask(__name__)

#@app.route('/')
#def hello_napier():
 #   return 'Hello Napier'

from app import app, db
with app.app_context():
    db.create_all()


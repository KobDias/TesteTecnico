from flask import Flask, url_for, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from db import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Cliente
import hashlib

app = Flask(__name__)
app.secret_key = "m04H4H4"
lm = LoginManager(app)
lm.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabeleleila.db'
db.init_app(app)

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@app.route('/')
def index():
    return render_template('header.html')



if __name__ == '__main__':
    app.run(debug=True)
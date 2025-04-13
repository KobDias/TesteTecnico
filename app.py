from flask import Flask, url_for, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from db import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Cliente
import hashlib

app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True)
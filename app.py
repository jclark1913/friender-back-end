import os
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort,
)
import boto3
from models import User, Message, Friendship, db, connect_db


s3 = boto3.client('s3')

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
#toolbar = DebugToolbarExtension(app)

connect_db(app)

########################

@app.route("/upload", methods=["POST"])
def upload_photo():
    """Test s3 bucket"""
    s3.upload_file("./testphoto.jpg", "friender-rithm-terrysli", "test.photos")


import os
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort, jsonify
)
from models import User, Message, Friendship, db, connect_db

import boto3



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

# /users routes

# GET all users (TODO: add admin protected middleware)
@app.route("/users", methods=["GET"])
def show_all_users():
    """Returns all users"""

    users = User.all()
    serialized = [u.serialize() for u in users]
    return jsonify(users=serialized)


# GET user by username (admin/loggedin/sameuser/friend?) NOTE: need to block rejected connections
@app.route("/users/<username>")
def get_user_by_username(username):
    """Returns given user"""

    user = User.get(username)

    serialized = user.serialize()

    return jsonify(user=serialized)


# POST create new user (register)
@app.route("/users", methods=["POST"])
def create_new_user():
    """Creates new user"""

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]
    location = request.json["location"]
    bio = request.json["bio"]
    friend_radius = request.json["friend_radius"]
    photo = request.json["photo"]
    is_admin = request.json["is_admin"]

    new_user = User.register(
        username=username,
        email=email,
        password=password,
        location=location,
        bio=bio,
        friend_radius=friend_radius,
        photo=photo,
        is_admin=is_admin
        )

    db.session.commit()

    serialized = new_user.serialize()
    return jsonify(user=serialized)


# PATCH edit user (admin/loggedin/sameuser)
@app.route("/users", method=["PATCH"])
def update_user():
    """Update user data"""



# DELETE user (admin/loggedin/sameuser)




# @app.route("/upload", methods=["POST"])
# def upload_photo():
#     """Test s3 bucket"""
#     s3.upload_file("./testphoto.jpg", "friender-rithm-terrysli", "test.photos")


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
    return (jsonify(user=serialized), 201)


# PATCH edit user (admin/loggedin/sameuser)
@app.route("/users/<username>", methods=["PATCH"])
def update_user(username):
    """Update user data"""

    if "email" in request.json: email = request.json["email"]
    if "location" in request.json: location = request.json["location"]
    if "bio" in request.json: bio = request.json["bio"]
    if "friend_radius" in request.json: friend_radius = request.json["friend_radius"]
    if "photo" in request.json: photo = request.json["photo"]
    if "is_admin" in request.json: is_admin = request.json["is_admin"]

    updated_user = User.update(username=username,
        email=email,
        location=location,
        bio=bio,
        friend_radius=friend_radius,
        photo=photo,
        is_admin=is_admin)

    db.session.commit()

    serialized = updated_user.serialize()
    return jsonify(user=serialized)


# DELETE user (admin/loggedin/sameuser)
@app.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    """Delete a user"""

    User.delete(username)
    db.session.commit()

    return jsonify({"deleted": username})



# @app.route("/upload", methods=["POST"])
# def upload_photo():
#     """Test s3 bucket"""
#     s3.upload_file("./testphoto.jpg", "friender-rithm-terrysli", "test.photos")


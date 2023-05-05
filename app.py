import os
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort, jsonify
)
from models import User, Message, Friendship, db, connect_db
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import boto3
from io import BytesIO

s3 = boto3.client('s3')

load_dotenv()

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
#toolbar = DebugToolbarExtension(app)
app.config['UPLOAD_FOLDER'] = "./temp"
app.config["JWT_SECRET_KEY"] = "super-secret" # TODO: Update .env

BUCKET_NAME = "friender-rithm-terrysli"
BUCKET_PUBLIC_PATH = "profile_photos"

connect_db(app)


def get_token(user):
    """Create access token for user"""

    token = create_access_token(
        identity=user.username,
        additional_claims={"is_admin": user.is_admin})
    return token


########## /auth routes

@app.route("/auth/login", methods=["POST"])
def login():
    """Log in user and return access token if valid username/password,
    otherwise return error message"""

    username = request.json["username"]
    password = request.json["password"]

    user = User.authenticate(username, password)
    if user:
        token = get_token(user)
        return jsonify(token=token)
    else:
        return jsonify({"Error": "Invalid username/password"}), 401


########## /users routes

# GET all users (ADMIN ONLY)
@app.route("/users", methods=["GET"])
@jwt_required()
def show_all_users():
    """Returns all users"""

    claims = get_jwt()
    if claims["is_admin"] == True:
        users = User.all()
        serialized = [u.serialize() for u in users]
        return jsonify(users=serialized)

    return jsonify({"Error": "This route is admin-protected"}), 401


# GET user by username (admin/loggedin/sameuser/friend?) TODO: need to block rejected connections
@app.route("/users/<username>")
@jwt_required()
def get_user_by_username(username):
    """Returns given user"""

    user = User.get(username)
    serialized = user.serialize()

    return jsonify(user=serialized)


# POST create new user (register) TODO: Validate info before making new user
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

    new_user = User.register(
        username=username,
        email=email,
        password=password,
        location=location,
        bio=bio,
        friend_radius=friend_radius,
        photo=photo,
        is_admin=False
        )

    db.session.commit()

    serialized = new_user.serialize()
    return jsonify(user=serialized), 201


# PATCH edit user (TODO: add middleware for admin/loggedin/sameuser)
@app.route("/users/<username>", methods=["PATCH"])
@jwt_required()
def update_user(username):
    """Update user data"""

    claims = get_jwt()
    identity = get_jwt_identity()

    if claims["is_admin"] == True or identity == username:
        data = request.json
        updated_user = User.update(username=username, data=data)

        serialized = updated_user.serialize()
        db.session.commit()

        return jsonify(user=serialized)

    return jsonify({"Error": "Unauthorized"}), 401


# DELETE user (TODO: add middleware for admin/loggedin/sameuser)
@app.route("/users/<username>", methods=["DELETE"])
@jwt_required()
def delete_user(username):
    """Delete a user"""

    claims = get_jwt()
    identity = get_jwt_identity()

    if claims["is_admin"] == True or identity == username:
        User.delete(username)
        db.session.commit()

        return jsonify({"deleted": username})

    return jsonify({"Error": "Unauthorized"}), 401

# GET friends of user TODO: Add middleware for same user/admin/loggedin
@app.route("/users/<username>/friends", methods=["GET"])
def get_friends_for_user(username):
    """Returns array of friends for user"""

    friends = User.friends(username)
    serialized = [f.serialize() for f in friends]

    return jsonify(friends=serialized)


# GET messages either sent or received by user
@app.route("/users/<username>/messages", methods=["GET"])
def get_user_messages(username):
    """Return array of messages involving user"""

    messages = User.messages(username)
    serialized = [m.serialize() for m in messages]

    return jsonify(messages=serialized)


########## /messages routes

@app.route("/messages", methods=["GET"])
#@jwt_required()
def get_all_messages():
    """Return data on all messages"""

    # claims = get_jwt()

    # if claims["is_admin"] == True:
    messages = Message.all()
    serialized = [m.serialize() for m in messages]

    return jsonify(messages=serialized)

    return jsonify({"Error": "Unauthorized"}), 401


# NOTE: needed?
@app.route("/messages/<int:message_id>", methods=["GET"])
def get_message_by_id(message_id):
    """Returns a message of a given id"""


    message = Message.get(message_id)
    serialized = message.serialize()

    return jsonify(message=serialized)

@app.route("/messages", methods=["POST"])
def create_new_message():
    """Create a new message"""

    from_user = request.json["from_user"]
    to_user = request.json["to_user"]
    text = request.json["text"]

    message = Message.create(from_user=from_user, to_user=to_user, text=text)
    serialized = message.serialize()

    db.session.commit()

    return jsonify(message=serialized)

####### /friendships

@app.route("/friendships", methods=["GET"])
def get_all_friendships():
    """Get all friendship data"""

    friendships = Friendship.all()

    serialized = [f.serialize() for f in friendships]

    return jsonify(friendships=serialized)

@app.route("/friendships/<int:friendship_id>", methods=["GET"])
def get_friendship_by_id(friendship_id):
    """Get friendship data by id"""

    friendship = Friendship.get(friendship_id)

    serialized = friendship.serialize()

    return jsonify(friendship=serialized)


@app.route("/friendships", methods=["POST"])
def send_friend_request():
    """Create new friendship request"""

    sender = request.json["sender"]
    recipient = request.json["recipient"]

    friendship = Friendship.create(sender, recipient)
    serialized = friendship.serialize()

    db.session.commit()

    return jsonify(friendship=serialized)

@app.route("/friendships/<int:friendship_id>", methods=["PATCH"])
def update_friend_request(friendship_id):
    """Update status of friendship with given id"""

    new_status = request.json["status"]

    updated_friendship = Friendship.change_status(friendship_id, new_status)
    serialized = updated_friendship.serialize()

    db.session.commit()

    return jsonify(friendship=serialized)

# Route to upload file to S3
@app.route('/url_route/<username>', methods=['POST'])
def upload_file(username):
    """Handles the upload of a file."""
    d = {}
    try:
        file = request.files['file_from_react']
        #breakpoint()
        filename = file.filename
        # with open(filename, "rb") as f:
        s3.upload_fileobj(file, BUCKET_NAME, f"{BUCKET_PUBLIC_PATH}/{username}_photo.jpeg", ExtraArgs={
            "ContentType":"image/jpeg"
        })

        # print(f"Uploading file {filename}")
        # file_bytes = file.read()
        # file_content = BytesIO(file_bytes).readlines()
        # print(file_content)
        d['status'] = 1

    except Exception as e:
        print(f"Couldn't upload file {e}")
        d['status'] = 0

    return jsonify(d)


# @app.route("/upload", methods=["POST"])
# def upload_photo():
#     """Test s3 bucket"""
#     s3.upload_file("./testphoto.jpg", "friender-rithm-terrysli", "test.photos")
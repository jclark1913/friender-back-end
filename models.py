"""SQLAlchemy models for Friender"""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in Friender"""

    __tablename__ = 'users'

    username = db.Column(
        db.Text,
        primary_key=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    hashed_password = db.Column(
        db.Text,
        nullable=False
    )

    location = db.Column(
        db.Integer,
        nullable=False
    )

    bio = db.Column(
        db.Text,
        nullable=False
    )

    friend_radius = db.Column(
        db.Integer,
        nullable=False
    )

    photo = db.Column(
        db.Text
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False
    )

    sent_messages = db.relationship(
        "Message", foreign_keys="Message.from_user", backref="sent_by"
    )

    received_messages = db.relationship(
        "Message", foreign_keys="Message.to_user", backref="received_by"
    )

    def serialize(self):
        """Serialize to dictionary"""

        return {
        "username": self.username,
        "email": self.email,
        "location": self.location,
        "bio": self.bio,
        "friend_radius": self.friend_radius,
        "photo": self.photo
        }

    #TODO: Figure out friends relationship

    # friends = db.relationship(
    #     # join on either user column
    #     # must be accepted friendship
    #     "Friendship",
    #     primaryjoin=(Friendship.sender == username)
    #     secondaryjoin=(Friendship.status == "accepted")

    #     # secondary="friendships",
    #     # primaryjoin=(Friendship.sender == username, Friendship.receiver == username),
    #     # secondaryjoin=()

    # )

    # outgoing_requests = db.relationship()

    # received_requests = db.relationship()

    @classmethod
    def register(cls, username, email, password, location, bio, friend_radius, photo, is_admin):
        """Registers new user and adds them to db"""

        hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            location=location,
            bio=bio,
            friend_radius=friend_radius,
            photo=photo,
            is_admin=is_admin
        )

        db.session.add(new_user)
        return new_user

    @classmethod
    def all():
        """Get all users"""

        users = User.query.all()

        return users

    @classmethod
    def get(username):
        """Get a specific user"""

        user = User.query.get_or_404(username)

        return user

    @classmethod
    def messages_from(username):
        """Get all messages from a user"""

        user = User.query.get_or_404(username)



#########  Message Class  ##########

class Message(db.Model):
    """Messages sent from one User to another"""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    text = db.Column(
        db.String(140),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    from_user = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    to_user = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )


class Friendship(db.Model):
    """A pending, accepted, or rejected friendship between 2 Users"""

    __tablename__ = 'friendships'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    sender = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    recipient = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False,
    )

    status = db.Column(
        db.Text,
        nullable=False
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)


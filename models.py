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




def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)


"""SQLAlchemy models for Friender"""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, join

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

    # recipient_friends = db.relationship(
    #     "User",
    #     secondary="friendships",
    #     primaryjoin="User.username==Friendship.sender",
    #     secondaryjoin="User.username==Friendship.recipient",
    #     backref="sender_friends"
    # )

    # sender_friends = db.relationship(
    #     "User",
    #     secondary="friendships",
    #     primaryjoin="User.username==Friendship.recipient",
    #     secondaryjoin="User.username==Friendship.sender",
    #     backref="recipient_friends"
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
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'.

        If user is found, check if stored hashed_password matches password.
        If yes, return user object, otherwise return false.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.hashed_password, password)
            if is_auth:
                return user

        return False


    @classmethod
    def all(cls):
        """Return all users"""

        users = User.query.all()

        return users


    @classmethod
    def get(cls, username):
        """Return a specific user"""

        user = User.query.get_or_404(username)

        return user


    @classmethod
    def update(cls, username, data):
        """Update data for a specific user"""

        updated_user = User.query.get_or_404(username)

        updated_user.email = data.get("email", updated_user.email)
        updated_user.location = data.get("location", updated_user.location)
        updated_user.bio = data.get("bio", updated_user.bio)
        updated_user.friend_radius = data.get("friend_radius", updated_user.friend_radius)
        updated_user.photo = data.get("photo", updated_user.photo)

        return updated_user


    @classmethod
    def delete(cls, username):
        """Delete a specific user from db"""

        user = User.query.get_or_404(username)
        db.session.delete(user)

        return username


    @classmethod
    def messages(cls, username):
        """Get all messages from a user"""

        sent_messages = db.session.query(Message)\
            .join(User, User.username == Message.from_user)\
            .filter(or_(Message.from_user == username, Message.to_user == username))\
            .all()
        received_messages = db.session.query(Message)\
            .join(User, User.username == Message.to_user)\
            .filter(or_(Message.from_user == username, Message.to_user == username))\
            .all()
        return sent_messages + received_messages


    @classmethod
    def friends(cls, username):
        """Return array of all accepted friends"""

        sender_friends = db.session.query(User)\
            .join(Friendship, User.username == Friendship.sender)\
            .filter(or_(Friendship.sender == username, Friendship.recipient == username),\
                Friendship.status == 'accepted',\
                Friendship.recipient == username)\
            .all()
        recipient_friends = db.session.query(User)\
            .join(Friendship, User.username == Friendship.recipient)\
            .filter(or_(Friendship.sender == username, Friendship.recipient == username),\
                Friendship.status == 'accepted',\
                Friendship.sender == username)\
            .all()
        return sender_friends + recipient_friends


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

    def serialize(self):
            """Serialize Message to dictionary"""

            return {
            "id": self.id,
            "text": self.text,
            "from_user": self.from_user,
            "to_user": self.to_user,
            }


    @classmethod
    def all(cls):
        """Return all messages"""
        messages = Message.query.all()

        return messages


    @classmethod
    def get(cls, id):
        """Return a specific message"""

        message = Message.query.get_or_404(id)

        return message

    @classmethod
    def create(cls, from_user, to_user, text):
        """Creates a new message"""

        message = Message(
            from_user = from_user,
            to_user = to_user,
            text = text
        )

        db.session.add(message)

        return message


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

    def serialize(self):
        """Serialize to dictionary"""

        return {
        "id": self.id,
        "sender": self.sender,
        "recipient": self.recipient,
        "status": self.status,
        }


    @classmethod
    def all(cls):
        """Returns all friendships"""

        friendships = Friendship.query.all()

        return friendships

    @classmethod
    def get(cls, id):
        """Returns friendship by id"""

        friendship = Friendship.query.get_or_404(id)

        return friendship

    @classmethod
    def create(cls, sender, recipient):
        """Create a friendship request"""

        friendship = Friendship(
            sender=sender,
            recipient=recipient,
            status="pending"
        )

        db.session.add(friendship)

        return friendship

    @classmethod
    def change_status(cls, id, status):
        """Change status of friendship request"""

        friendship = Friendship.query.get_or_404(id)
        friendship.status = status

        return friendship


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)


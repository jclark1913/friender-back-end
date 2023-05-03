"""Seed test users, messages, and friendships"""
import random
from app import app
from models import db, User, Message, Friendship, connect_db
from faker import Faker

fake = Faker()

RANDOM_TIMESTAMPS = ["2021-02-12 06:41:25.698388",
"2022-11-07 11:30:08.462462",
"2022-12-25 23:07:30.426382",
"2021-06-15 22:58:17.381448",
"2022-06-21 03:45:08.618140",
"2021-05-01 11:57:06.885442",
"2022-11-25 22:30:26.732439",
"2021-08-10 02:00:27.092119",
"2022-06-17 19:22:25.447009",
"2021-08-20 10:57:16.147237"]

db.session.rollback()
db.drop_all()
db.create_all()

# Seed users

user1 = User(
    username = "jdawg",
    email = "j@j.com",
    hashed_password = '$2b$12$9ZmCxLgbag8Beioi4FTsXeg89aFBqyWKyvoeqWYRe9LztTsZs/n2u',
    location=48197,
    bio=fake.sentence()
)

user2 = User(
    username = "Terehh",
    email = "T@T.com",
    hashed_password = '$2b$12$9ZmCxLgbag8Beioi4FTsXeg89aFBqyWKyvoeqWYRe9LztTsZs/n2u',
    location=48197,
    bio=fake.sentence()
)

user3 = User(
    username = fake.ssn(),
    email = fake.email(),
    hashed_password = '$2b$12$9ZmCxLgbag8Beioi4FTsXeg89aFBqyWKyvoeqWYRe9LztTsZs/n2u',
    location=fake.postcode(),
    bio=fake.sentence()
)
user4 = User(
    username = fake.ssn(),
    email = fake.email(),
    hashed_password = '$2b$12$9ZmCxLgbag8Beioi4FTsXeg89aFBqyWKyvoeqWYRe9LztTsZs/n2u',
    location=fake.postcode(),
    bio=fake.sentence()
)
user5 = User(
    username = fake.ssn(),
    email = fake.email(),
    hashed_password = '$2b$12$9ZmCxLgbag8Beioi4FTsXeg89aFBqyWKyvoeqWYRe9LztTsZs/n2u',
    location=fake.postcode(),
    bio=fake.sentence()
)

db.session.add_all([user1, user2, user3, user4, user5])
db.session.commit()
# seed messages
message1 = Message(
    id = 1,
    text = fake.sentence(),
    timestamp=random.choice(RANDOM_TIMESTAMPS),
    from_user = "jdawg",
    to_user = "Terehh"
)

message2 = Message(
    id = 2,
    text = fake.sentence(),
    timestamp=random.choice(RANDOM_TIMESTAMPS),
    from_user = "Terehh",
    to_user = "jdawg"
)

message3 = Message(
    id = 3,
    text = fake.sentence(),
    timestamp=random.choice(RANDOM_TIMESTAMPS),
    from_user = "jdawg",
    to_user = user4.username
)

db.session.add_all([message1, message2, message3])
db.session.commit()

# seed friendships

friendship1 = Friendship(
    id = 1,
    sender = "jdawg",
    recipient = "Terehh",
    status = "accepted"
)

friendship2 = Friendship(
    id = 2,
    sender = user3.username,
    recipient = user4.username,
    status = "pending"
)

friendship3 = Friendship(
    id = 3,
    sender = user4.username,
    recipient = user2.username,
    status = "accepted"
)

friendship4 = Friendship(
    id = 4,
    sender = user4.username,
    recipient = user5.username,
    status = "rejected"
)

db.session.add_all([friendship1, friendship2, friendship3, friendship4])
db.session.commit()
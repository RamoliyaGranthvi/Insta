from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User ( UserMixin, db.Model ):
    id = db.Column ( db.Integer, primary_key=True )
    username = db.Column ( db.String ( 80 ), unique=True, nullable=False )
    email = db.Column ( db.String ( 120 ), unique=True, nullable=True )
    password = db.Column ( db.String ( 255 ), nullable=False )
    number = db.Column ( db.String ( 15 ), unique=True, nullable=True )
    posts = db.relationship ( 'Post', backref='author', lazy=True )
    profiles = db.relationship ( 'Profile', backref='author', lazy=True )
    post_count = db.Column ( db.Integer, default=0 )

    # Updated the backref here to avoid conflict with the 'user' in Like
    likes = db.relationship ( 'Like', back_populates='user', lazy=True )

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Correct ForeignKey
    likes_count = db.Column(db.Integer, default=0, nullable=False)

    # Relationship with likes
    likes = db.relationship('Like', back_populates='post' , lazy=True )
    comments = db.relationship('Comment', back_populates='post', lazy=True)


class Profile(db.Model):
    id = db.Column ( db.Integer, primary_key=True )
    user_id = db.Column ( db.Integer, db.ForeignKey ( 'user.id' ), nullable=False )
    username = db.Column ( db.String ( 100 ))
    nickname = db.Column ( db.String ( 100 ), nullable=True )
    bio = db.Column ( db.Text, nullable=True )
    image_path = db.Column ( db.String ( 200 ), nullable=True )

    def __init__(self, nickname, bio, image_path, user_id):

        self.nickname = nickname
        self.bio = bio
        self.image_path = image_path
        self.user_id = user_id


class Comment ( db.Model ):
    id = db.Column ( db.Integer, primary_key=True )
    text = db.Column ( db.String ( 500 ), nullable=False )
    timestamp = db.Column ( db.DateTime, default=datetime.utcnow )

    user_id = db.Column ( db.Integer, db.ForeignKey ( 'user.id' ), nullable=False )
    post_id = db.Column ( db.Integer, db.ForeignKey ( 'post.id' ), nullable=False )

    user = db.relationship ( 'User', backref=db.backref ( 'comments', lazy=True ) )

    # Use back_populates to link this relationship to the Post model
    post = db.relationship ( 'Post', back_populates='comments', lazy=True )



class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Reference 'user.id'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))  # Reference 'post.id'

    # Updated the back_populates to match the new backref in the User model
    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')

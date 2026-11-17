from datetime import datetime
from typing import Any
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    images = db.relationship('ImageUpload', backref='user', lazy=True, cascade="all, delete-orphan")
    stories = db.relationship('Story', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }


class ImageUpload(db.Model):
    __tablename__ = 'uploaded_images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    scene_category = db.Column(db.String(120), nullable=True)
    detected_objects_json = db.Column(db.Text, nullable=True) # JSON array
    caption = db.Column(db.Text, nullable=True)
    diagnostics_json = db.Column(db.Text, nullable=True) # JSON diagnostics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    stories = db.relationship('Story', backref='image_upload', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_detected_objects(self):
        return json.loads(self.detected_objects_json) if self.detected_objects_json else []

    def get_diagnostics(self):
        return json.loads(self.diagnostics_json) if self.diagnostics_json else {}

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "filepath": self.filepath,
            "scene_category": self.scene_category,
            "caption": self.caption,
            "detected_objects": self.get_detected_objects(),
            "diagnostics": self.get_diagnostics(),
            "created_at": self.created_at.isoformat()
        }


class Story(db.Model):
    __tablename__ = 'generated_stories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    image_id = db.Column(db.Integer, db.ForeignKey('uploaded_images.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    length_mode = db.Column(db.String(50), nullable=False)
    tone = db.Column(db.String(50), nullable=False)
    ending = db.Column(db.String(50), nullable=False)
    story_json = db.Column(db.Text, nullable=False) # JSON complete story object
    relevance_json = db.Column(db.Text, nullable=True) # JSON relevance breakdown
    relevance_score = db.Column(db.Float, default=0.0)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    versions = db.relationship('StoryVersion', backref='story', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_story_data(self):
        return json.loads(self.story_json) if self.story_json else {}

    def get_relevance_data(self):
        return json.loads(self.relevance_json) if self.relevance_json else {}

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_id": self.image_id,
            "title": self.title,
            "genre": self.genre,
            "length_mode": self.length_mode,
            "tone": self.tone,
            "ending": self.ending,
            "story_data": self.get_story_data(),
            "relevance_score": self.relevance_score,
            "relevance_data": self.get_relevance_data(),
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat(),
            "image_path": self.image_upload.filepath if self.image_upload else None
        }


class StoryVersion(db.Model):
    __tablename__ = 'story_versions'

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('generated_stories.id'), nullable=False)
    version_name = db.Column(db.String(100), nullable=False) # e.g. "Adventure Version", "Mystery Version"
    genre = db.Column(db.String(50), nullable=False)
    story_json = db.Column(db.Text, nullable=False)
    relevance_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_story_data(self):
        return json.loads(self.story_json) if self.story_json else {}

    def to_dict(self):
        return {
            "id": self.id,
            "story_id": self.story_id,
            "version_name": self.version_name,
            "genre": self.genre,
            "story_data": self.get_story_data(),
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat()
        }

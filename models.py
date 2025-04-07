from db import db
import uuid
from sqlalchemy.dialects.postgresql import JSON
import json
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  
    role = db.Column(db.Enum("candidate", "recruiter", name="user_roles"), nullable=False)  
    resume_path = db.Column(db.String(255), default="")  
    skills = db.Column(db.JSON, default=[])

    def set_password(self, password):
        """Hash password before storing"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify hashed password"""
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        """Convert User object to JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "resume_path": self.resume_path,
            "skills": self.skills,
        }

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"


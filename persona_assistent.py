# app.py — simple Flask + SQLAlchemy + SQLite persona app
# Run: pip install flask flask_sqlalchemy
# Then: python app.py
from flask import Flask, request, jsonify, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
import json

# --- App / DB setup ---
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "personas.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Simple model ---
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String, nullable=True)
    job_title = db.Column(db.String, nullable=True)
    annual_income = db.Column(db.Float, nullable=True)
    interests = db.Column(db.String, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    is_ideal = db.Column(db.Boolean, nullable=True)
    reasons_json = db.Column(db.Text, nullable=True)  # store reasons as JSON text

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "country": self.country,
            "job_title": self.job_title,
            "annual_income": self.annual_income,
            "interests": self.interests,
            "score": self.score,
            "is_ideal": bool(self.is_ideal),
            "reasons": json.loads(self.reasons_json) if self.reasons_json else []
        }
        return data
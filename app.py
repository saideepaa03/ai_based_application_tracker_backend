from flask import Flask
from db import db
from config import Config
from routes import auth_bp,user_bp
from flask_cors import CORS
from mail import mail
import smtplib
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config.from_object(Config)  # Load config

db.init_app(app)
mail.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

CORS(app, origins=["http://localhost:5173"])
# with app.app_context():
#     db.drop_all()
#     db.create_all()

load_dotenv()

EMAIL = os.getenv("MAIL_USERNAME")
PASSWORD = os.getenv("MAIL_PASSWORD")

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("recruitertest58@gmail.com", "znuajqfnzcpuudlk" )
    print("✅ Successfully logged into Gmail SMTP!")
    server.quit()
except Exception as e:
    print(f"❌ Error: {e}")

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
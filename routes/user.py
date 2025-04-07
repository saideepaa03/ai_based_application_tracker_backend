import smtplib
from flask import jsonify, request, send_from_directory
from flask_mail import Message
from db import db
from models import User
from routes import user_bp  
import os
from werkzeug.utils import secure_filename
from pypdf import PdfReader 
from resumeparser import ats_extractor, getcheck
import json
from flask_mail import Message
from mail import mail
from pypdf.errors import PdfReadError
from docx import Document
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

test = """
Job Title: Python Developer
Location: Bangalore, India (Remote Available)
Job Type: Full-Time
Experience Level: 1-3 Years
Salary: ₹6,00,000 – ₹12,00,000 per annum
About the Company:

Tech Innovators Pvt. Ltd. is a fast-growing software company specializing in AI-based recruitment solutions. We develop cutting-edge Applicant Tracking Systems (ATS) powered by AI to help companies streamline hiring.
Job Overview:

We are looking for a Python Developer with experience in Flask/Django and PostgreSQL. The role involves building scalable APIs, integrating AI models, and optimizing our resume parsing system.
Key Responsibilities:

    Develop RESTful APIs using Flask/Django.
    Work with PostgreSQL to store and retrieve data efficiently.
    Implement resume ranking features using GPT-based AI models.
    Write clean, optimized, and well-documented code.
    Collaborate with the frontend team using React.js.
    Troubleshoot bugs and optimize application performance.

Required Skills:

✅ Programming: Python, JavaScript
✅ Backend: Flask, Django, FastAPI (Preferred)
✅ Database: PostgreSQL, MongoDB (Optional)
"""

UPLOAD_FOLDER = "uploads/resumes"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def _read_file_from_path(path):
    data = ""

    try:
        if path.endswith(".pdf"):
            with open(path, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        data += text

        elif path.endswith(".docx"):
            doc = Document(path)
            for para in doc.paragraphs:
                data += para.text + "\n"

        else:
            return {"error": "Unsupported file format"}, 400

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500

    return data


@user_bp.route("/all", methods=["GET"])
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "name": user.name, "email": user.email, "role": user.role} for user in users]
    return jsonify(users_list), 200

def add_skills_to_user(user_id, skills_list):
    """
    Add skills to a user's skill set.

    :param user_id: ID of the user.
    :param skills_list: List of new skills to be added.
    :return: Dictionary with success message or error.
    """
    user = User.query.get(user_id)
    if not user:
        return []

    if not isinstance(skills_list, list):
        return []

    # Merge new skills while avoiding duplicates
    user.skills = list(set(user.skills + skills_list))

    db.session.commit()
    return user.skills

def get_user_skills(user_id):
    """
    Get skills of a user.

    :param user_id: ID of the user.
    :return: Dictionary with skills or error.
    """
    user = User.query.get(user_id)
    if not user:
        return []

    return  user.skills

def upload_resume(user_id, file):
    """
    Uploads a resume file and saves the path in the database.

    :param user_id: ID of the user.
    :param file: Resume file object.
    :return: JSON response.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    # Validate file type
    if "." not in file.filename or file.filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return {"error": "Only PDF and DOCX files are allowed"}, 400

    filename = secure_filename(f"{user_id}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    data = _read_file_from_path(filepath)
    print("hello")
    print(data[0])
    data = ats_extractor(data[0])
    print("inside")
    print(data)
    # Update user resume path in database
    user.resume_path = filepath
    # data = json.loads(data)
    print(data.get("skills", []))
    user.skills = data.get("skills", [])
    # checkpercet(test,user.skills)
    db.session.commit()

    return {"message": "Resume uploaded successfully", "resume_path": filepath}, 200

@user_bp.route("/<id>/upload_resume", methods=["POST"])
def upload_resume_route(id):
    if "resume" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    response, status = upload_resume(id, file)
    return jsonify(response), status


def get_resume(user_id):
    """
    Returns the resume file of the user.

    :param user_id: ID of the user.
    :return: Resume file or error message.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if not user.resume_path or not os.path.exists(user.resume_path):
        return {"error": "Resume not found"}, 404

    return send_from_directory(os.path.dirname(user.resume_path), os.path.basename(user.resume_path), as_attachment=True)


@user_bp.route("/<id>/resume", methods=["GET"])
def get_resume_route(id):
    response = get_resume(id)
    return response

def checkpercet(desc, keyskill):
    match_result = getcheck(desc,resume_data=keyskill)
    print(match_result)
    # match_result = json.loads(match_result)
    print(match_result.get('percent'))
    return match_result.get('percent')

@user_bp.route("/process",methods = ['POST'])
def get_best():
    data = request.get_json()
    desc = data["desc"]
    # user = User.query.get()
    users = User.query.all()  # Fetch all users
    results = []

    for user in users:
        if user.resume_path:  # Ensure the user has a resume
            percent = checkpercet(desc, user.skills)
            results.append({"user_id": user.id, "percent": percent,"path":user.resume_path,"name":user.name,"email":user.email})

    # Sort users by percentage in descending order and get top 5
    top_users = sorted(results, key=lambda x: x["percent"], reverse=True)[:5]

    return jsonify(top_users)

def send_email_func(to_email, subject, message):
    try:
        # Create SMTP session
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure connection

        # Login to Gmail SMTP
        server.login("recruitertest58@gmail.com", "znuajqfnzcpuudlk" )

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = "recruitertest58@gmail.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Send email
        server.sendmail("recruitertest58@gmail.com", to_email, msg.as_string())

        # Close server connection
        server.quit()

        print(f"✅ Email sent successfully to {to_email}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")



    
@user_bp.route('/sendemail', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        print(user_id)
        # Fetch user from DB
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not user.email:
            return jsonify({"error": "User has no email"}), 400
        print(user.email)
        # Call the reusable send_mail function
        send_email_func(
            user.email, 
            "job update", 
            "Hi candidate, We are happy to inform you that your resume have been shortlisted"
        )

        return jsonify({"msg":"done"}), 200

    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500



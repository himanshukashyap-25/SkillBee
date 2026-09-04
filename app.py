from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from bson import ObjectId
from openai import OpenAI
import bcrypt
import os

# Import helper functions from models.py
from models import (
    get_courses, create_user, find_user_by_email,
    get_skills, get_skill_by_id,
    enroll_in_skill, get_tutorials,
    enroll_in_tutorial, seed_data,
    get_course_by_id
)


courses = [
    {
        "id": "1",
        "name": "Python Full Course",
        "description": "Beginner to Advanced Python programming.",
        "thumbnail": "https://cdn.analyticsvidhya.com/wp-content/uploads/2021/10/57202wallpaper.png",
        "category": "python",
        "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
        "content": [
            "Introduction to Python",
            "Variables & Data Types",
            "Loops & Conditionals",
            "Functions & Modules",
            "OOP in Python",
            "File Handling",
            "Projects"
        ]
    },
    {
        "id": "2",
        "name": "Java Complete Bootcamp",
        "description": "Learn Java from scratch with projects.",
        "thumbnail": "/static/java.png",
        "category": "java",
        "video_url": "https://www.youtube.com/embed/hBh_CC5y8-s",
        "content": [
            "Java Basics",
            "OOP Concepts",
            "Collections Framework",
            "Exception Handling",
            "Java Streams",
            "GUI with Swing",
            "Projects"
        ]
    }
]

# -------------------------
# BASIC SETUP
# -------------------------

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
admin_password = os.getenv('ADMIN_PASSWORD', 'Guruji0725')

client = MongoClient(mongo_uri)
db = client.skillbee

seed_data()

# -------------------------
# ROUTES
# -------------------------

@app.route('/')
def Home():
    return render_template('Home.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/teach')
def teach():
    tutorials = get_tutorials()  # Admin uploaded
    user_videos = list(db.user_uploaded.find())  # User uploaded
    return render_template('teach.html', tutorials=tutorials, user_videos=user_videos)
@app.route('/admin')
def admin():
    if session.get('admin_access'):
        return render_template('admin.html')
    return "Access Denied", 403



# -------------------------
# COURSE PAGES
# -------------------------

@app.route("/courses/programming")
def programming_courses():
    courses = get_courses(category="programming")
    return render_template("programming.html", courses=courses)

@app.route("/courses/uiux")
def uiux_courses():
    courses = get_courses(category="uiux")
    return render_template("uiux.html", courses=courses)

@app.route("/courses/webdev")
def webdev_courses():
    courses = get_courses(category="webdev")
    return render_template("webdev.html", courses=courses)

ALLOWED_VIDEO_EXT = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


UPLOAD_FOLDER_USER = "static/user_uploads/"
UPLOAD_FOLDER_USER_THUMB = "static/user_uploads/thumbnails/"

# Ensure folders exist
import os
os.makedirs(UPLOAD_FOLDER_USER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_USER_THUMB, exist_ok=True)







UPLOAD_FOLDER_THUMB = "static/thumbnails/"
UPLOAD_FOLDER_VIDEO = "static/videos/"

@app.route("/upload-user-video", methods=["POST"])
def upload_user_video():
    title = request.form.get("title")
    desc = request.form.get("desc")

    # Video file
    video = request.files.get("video")
    if not video or not allowed_file(video.filename, ALLOWED_VIDEO_EXT):
        return "Invalid video format", 400
    video_filename = secure_filename(video.filename)
    video.save(os.path.join(UPLOAD_FOLDER_USER, video_filename))
    
    # Thumbnail file
    thumb = request.files.get("thumbnail")
    if not thumb or not allowed_file(thumb.filename, ALLOWED_IMAGE_EXT):
        return "Invalid image format", 400
    thumb_filename = secure_filename(thumb.filename)
    thumb.save(os.path.join(UPLOAD_FOLDER_USER_THUMB, thumb_filename))

    # MongoDB insertion
    user_video = {
        "title": title,
        "description": desc,
        "video_url": "/static/user_uploads/" + video_filename,
        "thumbnail": "/static/user_uploads/thumbnails/" + thumb_filename
    }

    db.user_uploaded.insert_one(user_video)

    # Redirect to teach page
    return redirect(url_for("teach"))

    return redirect(url_for("teach"))







 






# -------------------------
# COURSE DETAIL PAGE (Udemy Style)
# -------------------------

@app.route("/course/<id>")
def course_detail(id):
    course = get_course_by_id(id)
    if not course:
        return "Course Not Found", 404
    return render_template("course.html", course=course)


# -------------------------
# SKILLS
# -------------------------

@app.route('/skill/<id>')
def skill_page(id):
    return render_template("skill_detail.html", skill_id=id)


# -------------------------
# TUTORIALS
# -------------------------
@app.route('/tutorial/<id>')
def tutorial_page(id):
    tutorial = get_tutorial_by_id(id)
    if not tutorial:
        return "Tutorial not found", 404
    return render_template("tutorial_detail.html", tutorial=tutorial)

@app.route("/debug/tutorial_ids")
def debug_ids():
    from models import get_tutorials
    data = get_tutorials()
    return {str(t["_id"]): t["title"] for t in data}


def get_tutorial_by_id(tutorial_id):
    try:
        # Try as ObjectId first
        return db.tutorials.find_one({'_id': ObjectId(tutorial_id)})
    except:
        # Fallback: check by string ID if needed
        tutorials = list(db.tutorials.find())
        for t in tutorials:
            if str(t["_id"]) == str(tutorial_id):
                return t
    return None

# -------------------------
# JOIN NOW
# -------------------------

@app.route('/join', methods=['POST'])
def join():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    enrolled_skills = request.form.getlist('enrolled_skills')

    if not all([full_name, email, password]):
        return jsonify({'success': False, 'message': 'All fields required'})

    if find_user_by_email(email):
        return jsonify({'success': False, 'message': 'Email already exists'})

    create_user(full_name, email, password, enrolled_skills)
    return jsonify({'success': True, 'message': 'User registered successfully!'})

# -------------------------
# LOGIN NOW
# -------------------------

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = find_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})

    # Check hashed password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'success': False, 'message': 'Incorrect password'})

    session['user_id'] = str(user['_id'])
    return jsonify({'success': True, 'message': 'Logged in successfully'})


# -------------------------
# SEARCH ENGINE
# -------------------------

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    skills = get_skills(query)
    tutorials = get_tutorials(query)

    results = (
        [{'id': str(s['_id']), 'name': s['name'], 'type': 'skill'} for s in skills] +
        [{'id': str(t['_id']), 'title': t['title'], 'type': 'tutorial'} for t in tutorials]
    )
    return jsonify(results)


# -------------------------
# ADMIN LOGIN
# -------------------------

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == admin_password:
            session['admin_access'] = True
            return redirect(url_for('admin'))
        return "Access Denied", 403

    return render_template("admin_login.html")


# -------------------------
# RUN APP
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)

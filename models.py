from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# CONNECT MONGO SAFE WAY
# -------------------------

MONGO_URI = os.getenv('MONGO_URI', "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.skillbee


# -------------------------
# USER FUNCTIONS
# -------------------------

# USER AUTO-INCREMENT COUNTER
def get_next_user_id():
    counter = db.counters.find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["value"]


# UPDATED USER CREATION FUNCTION
def create_user(full_name, email, password, enrolled_skills=None):
    if enrolled_skills is None:
        enrolled_skills = []

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Generate auto-incrementing user ID → USER0001
    user_number = get_next_user_id()
    user_primary_id = f"USER{user_number:04d}"

    return db.users.insert_one({
        'user_id': user_primary_id,
        'full_name': full_name,
        'email': email,
        'password': hashed,
        'enrolled_skills': enrolled_skills,
        'enrolled_tutorials': []
    })

# USER AUTO-INCREMENT COUNTER
def get_next_user_id():
    counter = db.counters.find_one_and_update(
        {"_id": "user_id"},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["value"]


def find_user_by_email(email):
    return db.users.find_one({'email': email})


# -------------------------
# SKILL FUNCTIONS
# -------------------------

def get_skills(query=None):
    if query:
        return list(db.skills.find(
            {'name': {'$regex': query, '$options': 'i'}}
        ).limit(5))
    
    return list(db.skills.find())


def get_skill_by_id(skill_id):
    try:
        return db.skills.find_one({'_id': ObjectId(skill_id)})
    except:
        return None


def enroll_in_skill(skill_id, user_id):
    try:
        skill_id = ObjectId(skill_id)
        user_id = ObjectId(user_id)
    except:
        return False

    db.skills.update_one({'_id': skill_id}, {'$addToSet': {'enrolled_users': user_id}})
    db.users.update_one({'_id': user_id}, {'$addToSet': {'enrolled_skills': skill_id}})
    return True


# -------------------------
# TUTORIAL FUNCTIONS
# -------------------------

def get_tutorials(query=None):
    if query:
        return list(db.tutorials.find(
            {'title': {'$regex': query, '$options': 'i'}}
        ).limit(5))
    
    return list(db.tutorials.find())


def get_tutorial_by_id(tutorial_id):
    try:
        return db.tutorials.find_one({'_id': ObjectId(tutorial_id)})
    except:
        return None


def enroll_in_tutorial(tutorial_id, user_id):
    try:
        tutorial_id = ObjectId(tutorial_id)
        user_id = ObjectId(user_id)
    except:
        return False

    db.tutorials.update_one({'_id': tutorial_id}, {'$addToSet': {'enrolled_users': user_id}})
    db.users.update_one({'_id': user_id}, {'$addToSet': {'enrolled_tutorials': tutorial_id}})
    return True

def get_tutorials(query=""):
    if query:
        # Case-insensitive search in title
        return list(db.tutorials.find({"title": {"$regex": query, "$options": "i"}}))
    return list(db.tutorials.find())


# -------------------------
# SEED DATA (ONLY IF EMPTY)
# -------------------------

def seed_data():
    if db.skills.count_documents({}) == 0:
        db.skills.insert_many([
            {
                'name': 'Programming',
                'description': 'Master programming languages like C, C++, Java, and Python.',
                'tools': ['C', 'C++', 'Java', 'Python'],
                'enrolled_users': []
            },
            {
                'name': 'UI/UX Design',
                'description': 'Learn Figma, Adobe XD and real UI/UX projects.',
                'tools': ['Figma', 'Adobe XD', 'Prototyping'],
                'enrolled_users': []
            },
            {
                'name': 'Web Development',
                'description': 'HTML, CSS, JavaScript, Bootstrap with projects.',
                'tools': ['HTML', 'CSS', 'Bootstrap', 'JavaScript'],
                'enrolled_users': []
            }
        ])

    if db.tutorials.count_documents({}) == 0:
        db.tutorials.insert_many([
            {
    'title': 'JavaScript Essentials',
    'description': 'DOM, ES6, functions, projects.',
    'video_url': 'https://www.youtube.com/embed/hdI2bqOjy3c',
    'thumbnail': '/static/thumbnails/js.png',
    'enrolled_users': []
},
{
    'title': 'Python for Beginners',
    'description': 'Syntax, loops, functions, logic.',
    'video_url': 'https://www.youtube.com/embed/rfscVS0vtbw',
    'thumbnail': '/static/thumbnails/python.png',
    'enrolled_users': []
},
{
    'title': 'Web Design Crash Course',
    'description': 'HTML, CSS, Bootstrap basics.',
    'video_url': 'https://www.youtube.com/embed/UB1O30fRSGg',
    'thumbnail': '/static/thumbnails/web.png',
    'enrolled_users': []
}

            
        ])

        
        if db.courses.count_documents({}) == 0:
         db.courses.insert_many([
        {
            "name": "Python Full Course",
            "description": "Learn Python from basics to advanced with notes, video & files.",
            "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
            "images": [
                "/static/python1.png",
                "/static/python2.png"
            ],
            "pdf_files": [
                "/static/python_notes.pdf"
            ],
            "word_files": [
                "/static/python_assignment.docx"
            ],
            "enrolled": 0
        },
        {
            "name": "Web Development Bootcamp",
            "description": "HTML, CSS, JavaScript complete course.",
            "video_url": "https://www.youtube.com/embed/UB1O30fRSGg",
            "images": [
                "/static/web1.png",
                "/static/web2.png"
            ],
            "pdf_files": [
                "/static/web_notes.pdf"
            ],
            "word_files": [
                "/static/web_assignment.docx"
            ],
            "enrolled": 0
        }
    ])
          # COURSES SEED (YAHI ADD KARNA HAI)
    
    if db.courses.count_documents({}) == 0:
       db.courses.insert_many([
        {
            "name": "Python Full Course",
            "description": "Beginner to Advanced",
            "thumbnail": "python.png",
            "category": "python",
            "video_url": "https://www.youtube.com/embed/rfscVS0vtbw"
        },
        {
            "name": "Java Complete Bootcamp",
            "description": "OOP + Projects",
            "thumbnail": "java.png",
            "category": "java",
            "video_url": "https://www.youtube.com/embed/hBh_CC5y8-s"
        },
        {
            "name": "C++ DSA Course",
            "description": "DSA + STL",
            "thumbnail": "cpp.png",
            "category": "cpp",
            "video_url": "https://www.youtube.com/embed/somecppvideo"
        }
    ])
    

def get_courses(category=None):
    query = {}

    if category:
        query["category"] = category

    return list(db.courses.find(query))


def get_course_by_id(course_id):
    try:
        return db.courses.find_one({"_id": ObjectId(course_id)})
    except:
        return None

        

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from sqlalchemy import text
import json

app = Flask(__name__, 
    static_folder='public', 
    static_url_path=''
)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",  
            "http://localhost:3001",  
            "http://localhost:3002", 
            "http://localhost:3003",  
            "http://localhost:5000",  
            "http://127.0.0.1:5000",  
            "http://172.31.4.143",     
            "http://3.128.255.245"     
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "User-Id"],
        "supports_credentials": True
    }
})

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

print(f"Database path: {os.path.join(basedir, 'users.db')}")

os.makedirs(basedir, exist_ok=True)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def serve_react_app():
    return send_from_directory('public', 'firstpage.html')

@app.route('/signup')
def serve_signup():
    return send_from_directory('public', 'signup.html')

@app.route('/login')
def serve_login():
    return send_from_directory('public', 'login.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        print("Received registration request with data:", data)

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            print("Missing required fields")
            return jsonify({"message": "Missing required fields"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists")
            return jsonify({"message": "User already exists!"}), 400

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(
                email=email,
                password=hashed_password,
                name=name
            )
            db.session.add(new_user)
            db.session.commit()
            
            print(f"Successfully created user: {email}")
            return jsonify({
                "message": "User registered successfully!",
                "user": {"email": email, "name": name}
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({"message": f"Database error: {str(e)}"}), 500

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"message": f"Registration error: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        print("Received login request with data:", data)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
            
        user = User.query.filter_by(email=email).first()
        print("Found user:", user)
        
        if not user:
            return jsonify({"message": "User not found"}), 401
            
        if not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid password"}), 401

        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
        
        response = jsonify({
            "message": "Login successful!",
            "user": user_data
        })
        
        origin = request.headers.get('Origin', '')
        domain = origin.split('://')[1].split(':')[0] if '://' in origin else 'localhost'
        print(f"Setting cookie for domain: {domain}")
        
        cookie_value = json.dumps(user_data)
        print(f"Setting cookie with value: {cookie_value}")
        
        response.set_cookie(
            'userData',
            value=cookie_value,
            max_age=604800,
            path='/',
            domain=domain,  
            samesite='None',  
            httponly=False,
            secure=False
        )
        
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        print(f"Response headers: {dict(response.headers)}")
        return response, 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"message": f"Login error: {str(e)}"}), 500

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
print(f"Upload folder path: {UPLOAD_FOLDER}")  

ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload folder: {UPLOAD_FOLDER}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"File saved to: {file_path}")
        if os.path.exists(file_path):
            print(f"File exists at: {file_path}")
            print(f"File size: {os.path.getsize(file_path)} bytes")
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename
        }), 200
    
    return jsonify({"message": "Invalid file type"}), 400

@app.route('/api/get-pdf/<filename>', methods=['GET'])
def get_pdf(filename):
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Attempting to serve file from: {file_path}")
        
        if os.path.exists(file_path):
            print(f"File found: {file_path}")
            print(f"File size: {os.path.getsize(file_path)} bytes")
            
            response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Cache-Control'] = 'no-cache'
            print("Response headers:", dict(response.headers))
            return response
        else:
            print(f"File not found: {file_path}")
            return jsonify({"message": "File not found"}), 404
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return jsonify({"message": f"Error serving file: {str(e)}"}), 500

def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables initialized successfully")

@app.route('/api/user-info', methods=['GET'])
def get_user_info():
    try:
        user_id = request.headers.get('User-Id')
        
        if not user_id:
            return jsonify({"message": "No user ID provided"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        response = jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        })
        
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response, 200

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    try:
        init_db()
        
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            print("Database connection successful")
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0',port=5000, debug=True)
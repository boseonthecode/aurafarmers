import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import shutil
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Configure Gemini AI
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Ensure directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.ORGANIZED_FOLDER, exist_ok=True)

# File to store custom directories
CUSTOM_DIRS_FILE = 'custom_directories.json'

def load_custom_directories():
    """Load custom directories from JSON file"""
    if os.path.exists(CUSTOM_DIRS_FILE):
        with open(CUSTOM_DIRS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_custom_directories(directories):
    """Save custom directories to JSON file"""
    with open(CUSTOM_DIRS_FILE, 'w') as f:
        json.dump(directories, f, indent=2)

def analyze_image_with_custom_dirs(image_path, custom_directories):
    """Use Gemini to analyze image and choose the best custom directory"""
    try:
        image = Image.open(image_path)
        
        if not custom_directories:
            # If no custom directories exist, return "uncategorized"
            return "uncategorized"
        
        # Create prompt with custom directories
        dir_list = "\n".join([f"- {name}: {desc}" for name, desc in custom_directories.items()])
        prompt = f"""
        Analyze this image and determine which of these custom directories it should be placed in:

        {dir_list}

        Based on the image content, return ONLY the directory name that best matches the image.
        If none of the directories are suitable, return "uncategorized".
        Return only the directory name, nothing else.
        """
        
        response = model.generate_content([prompt, image])
        result = response.text.strip().lower()
        
        # Validate if result matches any custom directory
        if result in [name.lower() for name in custom_directories.keys()]:
            return result
        
        # If no match or invalid response, return "uncategorized"
        return "uncategorized"
    
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return "uncategorized"

@app.route('/custom-directories', methods=['GET'])
def get_custom_directories():
    """Get all custom directories"""
    directories = load_custom_directories()
    return jsonify(directories)

@app.route('/custom-directories', methods=['POST'])
def create_custom_directory():
    """Create a new custom directory"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Directory name is required'}), 400
    
    name = data['name'].strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({'error': 'Directory name cannot be empty'}), 400
    
    # Load existing directories
    directories = load_custom_directories()
    
    # Check if directory already exists
    if name.lower() in [d.lower() for d in directories.keys()]:
        return jsonify({'error': 'Directory already exists'}), 400
    
    # Add new directory
    directories[name] = description
    save_custom_directories(directories)
    
    # Create physical directory
    dir_path = os.path.join(Config.ORGANIZED_FOLDER, name.lower())
    os.makedirs(dir_path, exist_ok=True)
    
    return jsonify({
        'success': True,
        'message': f'Directory "{name}" created successfully',
        'name': name,
        'description': description
    })

@app.route('/custom-directories/<directory_name>', methods=['DELETE'])
def delete_custom_directory(directory_name):
    """Delete a custom directory"""
    directories = load_custom_directories()
    
    # Find the directory (case-insensitive)
    actual_name = None
    for name in directories.keys():
        if name.lower() == directory_name.lower():
            actual_name = name
            break
    
    if not actual_name:
        return jsonify({'error': 'Directory not found'}), 404
    
    # Remove from custom directories
    del directories[actual_name]
    save_custom_directories(directories)
    
    # Remove physical directory if it exists and is empty
    dir_path = os.path.join(Config.ORGANIZED_FOLDER, directory_name.lower())
    try:
        if os.path.exists(dir_path):
            # Only remove if empty, otherwise just remove from custom list
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
            else:
                return jsonify({
                    'success': True,
                    'message': f'Directory "{actual_name}" removed from custom list (contains files)',
                    'warning': 'Physical directory contains files and was not deleted'
                })
    except Exception as e:
        print(f"Error removing directory: {e}")
    
    return jsonify({
        'success': True,
        'message': f'Directory "{actual_name}" deleted successfully'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Load custom directories
        custom_directories = load_custom_directories()
        
        # Analyze image with custom directories in mind
        category = analyze_image_with_custom_dirs(filepath, custom_directories)
        
        # Create category directory (either custom or uncategorized)
        category_dir = os.path.join(Config.ORGANIZED_FOLDER, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Move file to category directory
        new_filepath = os.path.join(category_dir, filename)
        counter = 1
        original_filename = filename
        
        # Handle duplicate filenames
        while os.path.exists(new_filepath):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            new_filepath = os.path.join(category_dir, filename)
            counter += 1
        
        shutil.move(filepath, new_filepath)
        
        # Check if this was a custom directory choice
        is_custom = category != "uncategorized"
        
        return jsonify({
            'success': True,
            'category': category,
            'filename': filename,
            'is_custom_directory': is_custom,
            'message': f'Image organized into {category} folder'
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all organized categories and their file counts"""
    categories = {}
    custom_directories = load_custom_directories()
    
    if os.path.exists(Config.ORGANIZED_FOLDER):
        for category in os.listdir(Config.ORGANIZED_FOLDER):
            category_path = os.path.join(Config.ORGANIZED_FOLDER, category)
            if os.path.isdir(category_path):
                file_count = len([f for f in os.listdir(category_path) 
                                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
                
                # Check if this is a custom directory
                is_custom = category.lower() in [name.lower() for name in custom_directories.keys()]
                
                categories[category] = {
                    'count': file_count,
                    'is_custom': is_custom,
                    'description': custom_directories.get(category, '') if is_custom else ''
                }
    
    return jsonify(categories)

@app.route('/category/<category_name>', methods=['GET'])
def get_category_files(category_name):
    """Get all files in a specific category"""
    category_path = os.path.join(Config.ORGANIZED_FOLDER, category_name)
    if not os.path.exists(category_path):
        return jsonify({'error': 'Category not found'}), 404
    
    files = [f for f in os.listdir(category_path) 
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    return jsonify({'files': files})

@app.route('/image/<category>/<filename>')
def serve_image(category, filename):
    """Serve organized images"""
    return send_from_directory(
        os.path.join(Config.ORGANIZED_FOLDER, category), 
        filename
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
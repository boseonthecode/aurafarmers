import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from pipeline import AITextSorterPipeline

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(BASE_DIR) / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

pipeline = AITextSorterPipeline()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'time': datetime.utcnow().isoformat(),
        'pipeline_ready': pipeline is not None
    })

@app.route('/api/process', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        return jsonify({'success': False, 'error': f'File type not allowed. Allowed: {allowed}'}), 400

    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        filepath = UPLOAD_FOLDER / unique_filename
        file.save(filepath)

        result = pipeline.process_document(str(filepath))

        # Optionally clean up the uploaded file after processing
        # os.remove(filepath)

        if result.get('success'):
            return jsonify({'success': True, 'data': result}), 200
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Processing failed')}), 500

    except Exception as e:
        logging.exception('Error processing document')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'success': False, 'error': f"File too large. Max size {MAX_FILE_SIZE // (1024*1024)} MB."}), 413

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Starting AI Text Sorter API server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)

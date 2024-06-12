from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
uploaded_files = []

def initialise():
    # Create upload folder if it does not exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Track all uploaded files on app startup
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            uploaded_files.append(filename)

initialise()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file while ensuring a safe filename
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/list-files', methods=['GET'])
def list_files():
    return jsonify({'files': uploaded_files}), 200

@app.route('/top_n_rows', methods=['GET'])
def top_n_rows():
    filename = request.args.get('filename')
    n = int(request.args.get('n'))
    sheet_name = request.args.get('sheet_name')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    # Secure the filename
    filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name if sheet_name else None)
        
        top_rows = df.head(n)
        return top_rows.to_json(orient='records'), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
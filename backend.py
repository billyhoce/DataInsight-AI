from flask import Flask, request
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file posted', 400
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    # Save file while ensuring a safe filename
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return 'File uploaded successfully', 200

if __name__ == '__main__':
    app.run(debug=True)
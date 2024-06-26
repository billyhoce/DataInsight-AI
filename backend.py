from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import pandas as pd
from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.responses.streamlit_response import StreamlitResponse
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
load_dotenv()
llm = OpenAI()

existing_file_names = []
existing_dataframes = []
prompt_history = []
smartDatalake = None

def is_accepted_file_type(filename):
    return filename.endswith('.csv') or filename.endswith('.xls') or filename.endswith('.xlsx')

def read_csv_excel_from_path(filename, filepath):
    if filename.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        return pd.read_excel(filepath)

def update_datalake():
    global smartDatalake
    smartDatalake = SmartDatalake(existing_dataframes, 
                                  config={"llm": llm, 
                                          "open_charts": False, 
                                          "save_charts": True, 
                                          "response_parser": StreamlitResponse})

def add_to_existing_files(filename, data):
    existing_file_names.append(filename)
    existing_dataframes.append(data)
    update_datalake()

def initialise():
    # Create upload folder if it does not exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Track all uploaded files on app startup
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):

        # Ignore all file types that are not CSV, XLS or XLSX
        if not is_accepted_file_type(filename):
            continue

        # Track existing files
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        existing_file_names.append(filename)
        existing_dataframes.append(read_csv_excel_from_path(filename, filepath))

    update_datalake()
    

initialise()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file while ensuring tha safe filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Add this new file into existing files for AI's use
    df = pd.read_csv(file_path) if filename.endswith('.csv') else pd.read_excel(file_path)
    add_to_existing_files(filename=filename, data=df)

    return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/list-files', methods=['GET'])
def list_files():
    return jsonify({'files': existing_file_names}), 200

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

@app.route('/ask_question', methods=['POST'])
def ask_question():
    question = request.json['question']
    try:
        answer = str(smartDatalake.chat(question))

        # Save the question and answer to history
        prompt_history.append({'question': question, 'answer': answer})

        # If the answer is path to image file
        if answer.endswith('.png'):
            return send_file(answer, mimetype='image/png')
    
        return jsonify({'answer': answer}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_prompt_history', methods=['GET'])
def get_prompt_history():
    return jsonify({'history': prompt_history}), 200

if __name__ == '__main__':
    app.run(debug=True, extra_files=[], use_reloader=False)
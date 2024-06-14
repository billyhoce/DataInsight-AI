import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

def upload_file_to_backend(file_to_upload):
    files = {'file': (file_to_upload.name, file_to_upload, file_to_upload.type)}
    response = requests.post("http://localhost:5000/upload", files=files)
    return response

def fetch_file_namelist():
    response = requests.get("http://localhost:5000/list-files")
    if response.status_code == 200:
        return response.json().get('files', [])
    else:
        st.error("Failed to fetch file list")
        return []
    
def display_top_n_rows(filename, n, container, sheet_name=None):
    params = {'filename': filename, 'n': n, 'sheet_name': sheet_name}
    response = requests.get("http://localhost:5000/top_n_rows", params=params)
    if response.status_code == 200:
        df = pd.read_json(response.text)
        container.write(df)
    else:
        st.error(f"Failed to fetch top {n} rows for {filename}")

def ask_question(question):
    response = requests.post("http://localhost:5000/ask_question", json={'question': question})
    if response.status_code == 200:
        if 'image/png' in response.headers.get('Content-Type', ''):
            return response.content, 'image'
        else:
            return response.json().get('answer', 'No answer returned'), 'text'
    else:
        st.error("Failed to get answer for the question")
        return None, None
    
def fetch_prompt_history():
    response = requests.get("http://localhost:5000/get_prompt_history")
    if response.status_code == 200:
        return response.json().get('history', [])
    else:
        st.error("Failed to fetch prompt history")
        return []

st.title(":red[Data Querying with PandasAI]")

files_col, chat_col = st.columns(2, gap="large")

with files_col:
    st.header("Data Overview")
    # Form for uploading of files
    with st.form("upload-form", clear_on_submit=True):
        new_files = st.file_uploader("Upload CSV/Excel files", type=['csv', 'xls', 'xlsx'], accept_multiple_files=True)
        submitted = st.form_submit_button()

        if submitted and new_files is not None:
            for new_file in new_files:
                upload_file_to_backend(new_file)

    # Display the list of uploaded files
    file_list = fetch_file_namelist()
    if file_list:
        selected_file = st.selectbox("Select a file to take a peek at", file_list)

        choose_row, choose_sheet = st.columns(2)
        with choose_row:
            n = st.number_input("Enter number of rows to display", min_value=1, step=1)
        with choose_sheet:
            sheet_name = st.text_input("Enter sheet name (if applicable)")
    
        if st.button("Take a peek", type="primary"):
            c = st.container(border=True)
            display_top_n_rows(selected_file, n, c, sheet_name)

with chat_col:
    # Allow users to enter prompt
    if file_list:
        st.header("Ask Questions About Your Datasets")
        prompt = st.text_area("Enter your prompt:")
        if st.button("Ask"):
            if prompt:
                answer = None
                answer_type = None
                with st.spinner("Generating your answer, please wait..."):
                    answer, answer_type = ask_question(prompt)
                if answer_type == 'image':
                    st.image(answer)
                else:
                    st.write(f"Answer: {answer}")
            else:
                st.warning("Please enter a prompt!")

        # Display Prompt History
        st.subheader("Prompt History")
        prompt_history = fetch_prompt_history()
        prompt_history.reverse()
        if prompt_history:
            with st.container(height=500):
                for idx, record in enumerate(prompt_history):
                    with st.container(border=True):
                        st.write(f":orange[Question: {record['question']}]  \nAnswer: {record['answer']}")
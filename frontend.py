import streamlit as st
import requests
import pandas as pd

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
    
def display_top_n_rows(filename, n, sheet_name=None):
    params = {'filename': filename, 'n': n, 'sheet_name': sheet_name}
    response = requests.get("http://localhost:5000/top_n_rows", params=params)
    if response.status_code == 200:
        df = pd.read_json(response.text)
        st.write(df)
    else:
        st.error(f"Failed to fetch top {n} rows for {filename}")

def ask_question(question):
    response = requests.post("http://localhost:5000/ask_question", json={'question': question})
    if response.status_code == 200:
        return response.json().get('answer', 'No answer returned')
    else:
        st.error("Failed to get answer for the question")
        return None

st.title("Data Querying with PandasAI")

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
    st.subheader("Uploaded Files")
    selected_file = st.selectbox("Select a file to display top N rows", file_list)
    n = st.number_input("Enter number of rows to display", min_value=1, step=1)
    sheet_name = st.text_input("Enter sheet name (if applicable)")
    if st.button("Display Top N Rows"):
        display_top_n_rows(selected_file, n, sheet_name)

# Allow users to enter prompt
if file_list:
    st.subheader("Ask Questions")
    prompt = st.text_area("Enter your prompt:")
    if st.button("Ask"):
        if prompt:
            answer = ask_question(prompt)
            st.write(f"Answer: {answer}")
        else:
            st.warning("Please enter a prompt!")

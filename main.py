import streamlit as st
import os
import base64
from io import BytesIO
from streamlit_ace import st_ace
from streamlit_option_menu import option_menu
from weasyprint import HTML
import markdown

st.set_page_config(page_title="Modern Markdown Viewer", layout="wide")

# Custom CSS for dark mode and styling
st.markdown("""
<style>
    /* Light mode styles */
    .stApp {
        background-color: #f0f2f6;
        color: #262730;
        transition: all 0.3s ease;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    /* Dark mode styles */
    .dark-mode .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .dark-mode .stTextInput > div > div > input {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    .dark-mode .stTextArea > div > div > textarea {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    /* Custom button styles */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# Dark mode toggle
def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# File handling functions
def save_file(name, content):
    st.session_state.files[name] = content

def delete_file(name):
    if name in st.session_state.files:
        del st.session_state.files[name]
    if st.session_state.current_file == name:
        st.session_state.current_file = None

def render_markdown(text):
    return markdown.markdown(text, extensions=['extra', 'codehilite'])

def generate_pdf(html_content):
    pdf = HTML(string=html_content).write_pdf()
    return pdf

def get_binary_file_downloader_html(bin_file, file_label='File'):
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">Download {file_label}</a>'
    return href

# Sidebar
with st.sidebar:
    st.title("Modern Markdown Viewer")
    
    # Dark mode toggle
    dark_mode = st.checkbox("Dark Mode", value=st.session_state.dark_mode, on_change=toggle_dark_mode)
    
    # File uploader
    uploaded_files = st.file_uploader("Choose Markdown file(s)", accept_multiple_files=True, type=['md'])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = uploaded_file.getvalue().decode("utf-8")
            save_file(uploaded_file.name, content)
    
    # File selection
    if st.session_state.files:
        st.session_state.current_file = st.selectbox("Select a file", list(st.session_state.files.keys()))

# Main content
if st.session_state.dark_mode:
    st.markdown('<div class="dark-mode">', unsafe_allow_html=True)

if st.session_state.current_file:
    # Tabs for Edit and Preview
    tab1, tab2 = st.tabs(["Edit", "Preview"])
    
    with tab1:
        content = st_ace(value=st.session_state.files[st.session_state.current_file], language="markdown", theme="monokai" if st.session_state.dark_mode else "github")
        if st.button("Save Changes"):
            save_file(st.session_state.current_file, content)
            st.success("Changes saved successfully!")
    
    with tab2:
        rendered_content = render_markdown(st.session_state.files[st.session_state.current_file])
        st.markdown(rendered_content, unsafe_allow_html=True)
        
        if st.button("Print as PDF"):
            pdf = generate_pdf(rendered_content)
            st.markdown(get_binary_file_downloader_html(pdf, f"{st.session_state.current_file}.pdf"), unsafe_allow_html=True)

    # Delete file button
    if st.button("Delete File"):
        delete_file(st.session_state.current_file)
        st.success(f"File '{st.session_state.current_file}' deleted successfully!")
else:
    st.info("Please upload or select a Markdown file to get started.")

if st.session_state.dark_mode:
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("Created with Streamlit | Modern Markdown Viewer")

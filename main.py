import streamlit as st
import os
import base64
from io import BytesIO
from streamlit_ace import st_ace
import markdown
from pygments.formatters import HtmlFormatter
from datetime import datetime
import json

st.set_page_config(page_title="Modern Markdown Viewer", layout="wide")

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary-color: #6200EA;
        --secondary-color: #03DAC6;
        --background-color: #FFFFFF;
        --text-color: #333333;
        --sidebar-color: #F5F5F5;
    }
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Roboto', sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: var(--sidebar-color);
    }
    h1, h2, h3 {
        color: var(--primary-color);
    }
    .stButton>button {
        background-color: var(--primary-color);
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
        background-color: var(--secondary-color);
    }
    /* Syntax highlighting styles */
    ${HtmlFormatter(style="github").get_style_defs('.highlight')}
    /* Floating action button */
    .floating-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 100;
    }
    /* Smooth transitions */
    * {
        transition: all 0.3s ease;
    }
    /* File list styling */
    .file-list {
        background-color: #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .file-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 10px;
        margin: 5px 0;
        background-color: white;
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }
    .file-name {
        font-weight: bold;
    }
    .file-size {
        color: #666;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'file_history' not in st.session_state:
    st.session_state.file_history = {}

# File handling functions
def save_file(name, content):
    st.session_state.files[name] = content
    if name not in st.session_state.file_history:
        st.session_state.file_history[name] = []
    st.session_state.file_history[name].append({
        'content': content,
        'timestamp': datetime.now().isoformat()
    })

def delete_file(name):
    if name in st.session_state.files:
        del st.session_state.files[name]
    if name in st.session_state.file_history:
        del st.session_state.file_history[name]
    if st.session_state.current_file == name:
        st.session_state.current_file = None

def render_markdown(text):
    return markdown.markdown(text, extensions=['extra', 'codehilite', 'tables', 'sane_lists', 'toc', 'fenced_code'])

def generate_pdf(html_content):
    # Placeholder for PDF generation
    return b"PDF content"

def get_binary_file_downloader_html(bin_file, file_label='File'):
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}" class="stButton">Download {file_label}</a>'
    return href

def display_file_list(files):
    st.markdown("<div class='file-list'>", unsafe_allow_html=True)
    for file in files:
        st.markdown(f"""
        <div class='file-item'>
            <span class='file-name'>{file.name}</span>
            <span class='file-size'>{file.size} bytes</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Markdown Viewer")
    
    # File uploader
    uploaded_files = st.file_uploader("Choose Markdown file(s)", accept_multiple_files=True, type=['md'])
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s)")
        display_file_list(uploaded_files)
        
        # Search/filter function
        search_term = st.text_input("Search files", "")
        filtered_files = [file for file in uploaded_files if search_term.lower() in file.name.lower()]
        
        if search_term:
            st.write(f"Found {len(filtered_files)} matching file(s)")
            display_file_list(filtered_files)
        
        for uploaded_file in uploaded_files:
            content = uploaded_file.getvalue().decode("utf-8")
            save_file(uploaded_file.name, content)
    
    # File selection
    if st.session_state.files:
        st.session_state.current_file = st.selectbox("Select a file", list(st.session_state.files.keys()))
    
    # Edit mode toggle
    if st.session_state.current_file:
        st.session_state.edit_mode = st.checkbox("Edit Mode", value=st.session_state.edit_mode)
    
    # PDF generation
    if st.session_state.current_file:
        if st.button("Generate PDF"):
            with st.spinner("Generating PDF..."):
                pdf = generate_pdf(render_markdown(st.session_state.files[st.session_state.current_file]))
                st.markdown(get_binary_file_downloader_html(pdf, f"{st.session_state.current_file}.pdf"), unsafe_allow_html=True)
                st.success("PDF generated successfully!")

# Main content
if st.session_state.current_file:
    if st.session_state.edit_mode:
        # Edit mode
        content = st_ace(value=st.session_state.files[st.session_state.current_file], language="markdown", theme="github")
        if st.sidebar.button("Save Changes"):
            save_file(st.session_state.current_file, content)
            st.sidebar.success("Changes saved successfully!")
    else:
        # View mode
        rendered_content = render_markdown(st.session_state.files[st.session_state.current_file])
        st.markdown(rendered_content, unsafe_allow_html=True)
    
    # Floating action buttons
    st.markdown(
        f"""
        <div class="floating-button">
            <button onclick="document.querySelector('.streamlit-expanderHeader').click()">{'📝' if not st.session_state.edit_mode else '👁️'}</button>
        </div>
        """,
        unsafe_allow_html=True
    )

    # File history
    with st.sidebar.expander("Version History"):
        history = st.session_state.file_history.get(st.session_state.current_file, [])
        for i, version in enumerate(reversed(history)):
            if st.button(f"Restore Version {len(history) - i}: {version['timestamp']}"):
                st.session_state.files[st.session_state.current_file] = version['content']
                st.success(f"Restored to Version {len(history) - i}")
                st.experimental_rerun()

else:
    st.info("Please upload or select a Markdown file to get started.")

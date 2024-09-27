import streamlit as st
import markdown2
from streamlit_ace import st_ace

st.set_page_config(page_title="Modern Markdown Viewer", layout="wide")

# Custom CSS for modern styling with dark mode
st.markdown("""
<style>
    /* Dark mode color scheme */
    :root {
        --primary-color: #BB86FC;
        --secondary-color: #03DAC6;
        --background-color: #121212;
        --surface-color: #1E1E1E;
        --text-color: #E0E0E0;
        --sidebar-color: #1A1A1A;
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
        color: var(--background-color);
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
    /* Syntax highlighting styles with darker background */
    .highlight {
        background-color: #2B2B2B;
        color: #A9B7C6;
        padding: 10px;
        border-radius: 5px;
    }
    /* Ensure line breaks are respected */
    .markdown-body p {
        white-space: pre-wrap;
    }
    /* File list styling */
    .file-list {
        background-color: var(--surface-color);
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .file-item {
        padding: 5px 10px;
        margin: 5px 0;
        background-color: var(--background-color);
        border-radius: 3px;
        cursor: pointer;
        color: var(--text-color);
    }
    .file-item:hover {
        background-color: var(--primary-color);
        color: var(--background-color);
    }
    .file-item-active {
        background-color: var(--primary-color);
        color: var(--background-color);
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
if 'editor_content' not in st.session_state:
    st.session_state.editor_content = ''
if 'last_edited_file' not in st.session_state:
    st.session_state.last_edited_file = None

# File handling functions
def save_file(name, content):
    st.session_state.files[name] = content

def render_markdown(text):
    return markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'task_list', 'highlightjs-lang', 'underscore'])

# Sidebar
with st.sidebar:
    st.title("Markdown Viewer")
    
    # File uploader
    uploaded_files = st.file_uploader("Choose Markdown file(s)", accept_multiple_files=True, type=['md'])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = uploaded_file.getvalue().decode("utf-8")
            save_file(uploaded_file.name, content)
    
    # Display file list and total count
    st.markdown(f"<h3>Files ({len(st.session_state.files)})</h3>", unsafe_allow_html=True)
    
    if st.session_state.files:
        # Use st.radio for file selection
        selected_file = st.radio(
            label="Select a file",
            options=list(st.session_state.files.keys()),
            index=list(st.session_state.files.keys()).index(st.session_state.current_file) if st.session_state.current_file else 0,
            key='file_selector'
        )
        if selected_file != st.session_state.current_file:
            st.session_state.current_file = selected_file
            st.session_state.edit_mode = False
    else:
        st.info("No files uploaded yet.")

    # Edit mode toggle
    if st.session_state.current_file:
        st.session_state.edit_mode = st.checkbox("Edit Mode", value=st.session_state.edit_mode)

# Main content
if st.session_state.files:
    if st.session_state.current_file:
        # Display single file content
        content = st.session_state.files[st.session_state.current_file]
        
        if st.session_state.edit_mode:
            # Initialize editor_content if the file has changed
            if st.session_state.last_edited_file != st.session_state.current_file:
                st.session_state.editor_content = content
                st.session_state.last_edited_file = st.session_state.current_file
            
            st.session_state.editor_content = st_ace(
                value=st.session_state.editor_content,
                language="markdown",
                theme="monokai",
                key=f"editor_{st.session_state.current_file}"
            )
            if st.button("Save Changes"):
                save_file(st.session_state.current_file, st.session_state.editor_content)
                st.success("Changes saved successfully!")
                st.session_state.edit_mode = False
                # Reset editor content
                st.session_state.editor_content = ''
                st.session_state.last_edited_file = None
        else:
            rendered_content = render_markdown(content)
            st.markdown(rendered_content, unsafe_allow_html=True)
    else:
        st.info("Select a file from the sidebar to view its content.")
else:
    st.info("Upload Markdown files using the sidebar to view and edit their content.")

# Keyboard navigation
if st.session_state.files:
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'ArrowRight') {
            nextFile();
        } else if (e.ctrlKey && e.key === 'ArrowLeft') {
            prevFile();
        }
    });
    
    function nextFile() {
        const options = document.querySelectorAll('input[type="radio"]');
        const selected = Array.from(options).findIndex(radio => radio.checked);
        if (selected < options.length - 1) {
            options[selected + 1].click();
        }
    }
    
    function prevFile() {
        const options = document.querySelectorAll('input[type="radio"]');
        const selected = Array.from(options).findIndex(radio => radio.checked);
        if (selected > 0) {
            options[selected - 1].click();
        }
    }
    </script>
    """, unsafe_allow_html=True)

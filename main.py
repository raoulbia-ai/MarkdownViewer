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
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: var(--surface-color);
        border-radius: 4px 4px 0 0;
        gap: 4px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: var(--text-color);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: var(--background-color);
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
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 10px;
        margin: 5px 0;
        background-color: var(--background-color);
        border-radius: 3px;
    }
    .file-name {
        font-weight: bold;
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'compare_mode' not in st.session_state:
    st.session_state.compare_mode = False
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []

# File handling functions
def save_file(name, content):
    st.session_state.files[name] = content

def render_markdown(text):
    return markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'task_list', 'highlightjs-lang'])

# Sidebar
with st.sidebar:
    st.title("Markdown Viewer")
    
    # File uploader
    uploaded_files = st.file_uploader("Choose Markdown file(s)", accept_multiple_files=True, type=['md'])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = uploaded_file.getvalue().decode("utf-8")
            save_file(uploaded_file.name, content)
    
    # Search/filter function
    search_term = st.text_input("Search files", "")
    filtered_files = [file for file in st.session_state.files.keys() if search_term.lower() in file.lower()]
    
    # Display file list
    st.markdown("<div class='file-list'>", unsafe_allow_html=True)
    for file in filtered_files:
        st.markdown(f"""
        <div class='file-item'>
            <span class='file-name'>{file}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # File selection for comparison
    st.session_state.selected_files = st.multiselect("Select files for comparison", list(st.session_state.files.keys()), max_selections=2)
    
    # Compare mode toggle
    st.session_state.compare_mode = st.checkbox("Compare Mode", value=st.session_state.compare_mode)
    
    # Edit mode toggle
    st.session_state.edit_mode = st.checkbox("Edit Mode", value=st.session_state.edit_mode)
    
    # Save button in edit mode
    if st.session_state.edit_mode:
        if st.button("Save Changes"):
            st.session_state.edit_mode = False
            st.success("Changes saved successfully! Switched to render mode.")
            st.rerun()

# Main content
if st.session_state.files:
    if st.session_state.compare_mode and len(st.session_state.selected_files) == 2:
        # Side-by-side comparison
        col1, col2 = st.columns(2)
        for i, file_name in enumerate(st.session_state.selected_files):
            content = st.session_state.files[file_name]
            with col1 if i == 0 else col2:
                st.subheader(file_name)
                if st.session_state.edit_mode:
                    new_content = st_ace(value=content, language="markdown", theme="monokai", key=f"editor_{file_name}")
                    st.session_state.files[file_name] = new_content
                else:
                    rendered_content = render_markdown(content)
                    st.markdown(rendered_content, unsafe_allow_html=True)
    else:
        # Regular tab view
        tabs = st.tabs(list(st.session_state.files.keys()))
        for i, (file_name, content) in enumerate(st.session_state.files.items()):
            with tabs[i]:
                if st.session_state.edit_mode:
                    new_content = st_ace(value=content, language="markdown", theme="monokai", key=f"editor_{file_name}")
                    st.session_state.files[file_name] = new_content
                else:
                    rendered_content = render_markdown(content)
                    st.markdown(rendered_content, unsafe_allow_html=True)
else:
    st.empty()  # Blank main area when no files are uploaded

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
        display: block;
        padding: 5px 10px;
        margin: 5px 0;
        background-color: var(--background-color);
        border-radius: 3px;
        cursor: pointer;
        text-decoration: none;
        color: var(--text-color);
    }
    .file-item:hover {
        background-color: var(--primary-color);
        color: var(--background-color);
    }
    .file-item.active {
        background-color: var(--primary-color);
        color: var(--background-color);
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
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# File handling functions
def save_file(name, content):
    st.session_state.files[name] = content

def render_markdown(text):
    return markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'task_list', 'highlightjs-lang'])

def remove_file(name):
    if name in st.session_state.files:
        del st.session_state.files[name]
    if name in st.session_state.selected_files:
        st.session_state.selected_files.remove(name)
    if st.session_state.current_file == name:
        st.session_state.current_file = None

# Sidebar
with st.sidebar:
    st.title("Markdown Viewer")
    
    # File uploader
    uploaded_files = st.file_uploader("Choose Markdown file(s)", accept_multiple_files=True, type=['md'])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = uploaded_file.getvalue().decode("utf-8")
            save_file(uploaded_file.name, content)
    
    # Display file list
    st.markdown("<div class='file-list'>", unsafe_allow_html=True)
    for file in st.session_state.files.keys():
        active_class = "active" if file == st.session_state.current_file else ""
        st.markdown(f"<a href='#' class='file-item {active_class}' onclick=\"streamlit.setComponentValue('{file}')\">{file}</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # File management options
    if st.session_state.files:
        if st.button("Clear All Files"):
            st.session_state.files.clear()
            st.session_state.selected_files.clear()
            st.session_state.current_file = None
            st.rerun()
    
    # File selection for comparison
    st.session_state.selected_files = st.multiselect("Select files for comparison", list(st.session_state.files.keys()), max_selections=2)
    
    # Compare mode toggle
    if len(st.session_state.selected_files) == 2:
        if st.button("Compare Selected Files"):
            st.session_state.compare_mode = True
            st.session_state.current_file = None
    
    # Edit mode toggle
    st.session_state.edit_mode = st.checkbox("Edit Mode", value=st.session_state.edit_mode)
    
    # Save button in edit mode
    if st.session_state.edit_mode and st.session_state.current_file:
        if st.button("Save Changes"):
            st.success("Changes saved successfully!")
            st.session_state.edit_mode = False
            st.rerun()

# Handle file selection
if st.session_state.files:
    selected_file = st.session_state.get("selected_file")
    if selected_file:
        st.session_state.current_file = selected_file
        st.session_state.compare_mode = False
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
    elif st.session_state.current_file:
        # Display single file content
        content = st.session_state.files[st.session_state.current_file]
        st.subheader(st.session_state.current_file)
        if st.button("Remove File"):
            remove_file(st.session_state.current_file)
            st.rerun()
        if st.session_state.edit_mode:
            new_content = st_ace(value=content, language="markdown", theme="monokai", key=f"editor_{st.session_state.current_file}")
            st.session_state.files[st.session_state.current_file] = new_content
        else:
            rendered_content = render_markdown(content)
            st.markdown(rendered_content, unsafe_allow_html=True)
    else:
        st.info("Select a file from the sidebar to view its content.")
else:
    st.empty()  # Blank main area when no files are uploaded

# Keyboard navigation
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
    var files = document.querySelectorAll('.file-item');
    var currentIndex = Array.from(files).findIndex(f => f.classList.contains('active'));
    if (currentIndex < files.length - 1) {
        files[currentIndex + 1].click();
    }
}

function prevFile() {
    var files = document.querySelectorAll('.file-item');
    var currentIndex = Array.from(files).findIndex(f => f.classList.contains('active'));
    if (currentIndex > 0) {
        files[currentIndex - 1].click();
    }
}
</script>
""", unsafe_allow_html=True)

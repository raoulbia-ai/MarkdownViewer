import streamlit as st

st.set_page_config(page_title="Markdown Viewer", layout="wide")

st.title("Markdown Viewer")

# File uploader
uploaded_file = st.file_uploader("Choose a Markdown file", type=['md'])

if uploaded_file is not None:
    content = uploaded_file.getvalue().decode("utf-8")
    st.markdown(content)
else:
    st.info("Please upload a Markdown file to get started.")

st.markdown("---")
st.markdown("Created with Streamlit")

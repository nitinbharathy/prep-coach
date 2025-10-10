import streamlit as st
from backend import parse_resume, match_to_jd  # UNCOMMENT THIS LINE WHEN YOUR BACKEND.PY IS READY:

# Initial setup
print("🚀 Starting chatbot...")

if 'resumeparsed' not in st.session_state:
    st.session_state.resumeparsed = False

def step1done():
    st.session_state.resumeparsed = True

# Configure the web page appearance
st.set_page_config(page_title="Interview App", page_icon="💼")
st.title("Welcome to the Interview App")

# Create text input area for user messages
input_resume = st.text_area("Paste your CV:", height=300)


parsed_resume=""
prev_resp_id=""
response2=""
prev_resp_id2=""

# Handle send button click
if st.button("📤 Go to Step 2", on_click=step1done) and input_resume:
    with st.spinner("Parsing your resume..."):
        parsed_resume,prev_resp_id = parse_resume(input_resume)

    # Display the conversation
    #st.markdown("**You:**")
    #st.write(input_resume)

    #st.markdown("**AI raw:**")
    # st.write(response)
    st.markdown("**AI JSON:**")
    st.json(parsed_resume, expanded=False)
    #resumeparsed=True

if st.session_state.resumeparsed:
    input_jd=st.text_area("Paste the JD:", height=300)

    if st.button("📤 Generate matches") and input_jd:
        print("button clicked")
        with st.spinner("Finding Job match..."):
            response2, prev_resp_id2 = match_to_jd(input_jd, parsed_resume, prev_resp_id)
            print("got response clicked")

        st.markdown("**AI JSON:**")
        st.json(response2, expanded=True)


    
    
    
    
    
# --- Show Latest Commit Message ---
# This snippet displays the last commit message at the bottom-right of the Streamlit app.
# It first checks if a 'commit.txt' file exists (useful for deployments),
# otherwise it falls back to reading the latest commit from git.
# If neither is available, it shows a default message.
# No need to deep dive – just a simple way to know what version of code is running.


import subprocess, os
from pathlib import Path
 
st.markdown(f"<div style='position:fixed; bottom:20px; right:20px; color:gray; font-size:15px; opacity:0.8;'>{(Path(__file__).parent / 'commit.txt').read_text().strip() if (Path(__file__).parent / 'commit.txt').exists() else subprocess.getoutput('git log -1 --pretty=%B') if os.path.exists(Path(__file__).parent / '.git') else 'No commit info'}</div>", unsafe_allow_html=True)
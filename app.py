import streamlit as st
from backend import parse_resume, match_to_jd, transcribe_audio, rate_answer  # UNCOMMENT THIS LINE WHEN YOUR BACKEND.PY IS READY:
import fitz # PyMuPDF
import json

# Initial setup
# Activate the virtual environment:
#   `.\myenv\Scripts\Activate`
# 
print("🚀 Starting chatbot...")

# Initialise and persist
if 'resumeparsed' not in st.session_state:
    st.session_state.resumeparsed = False
    st.session_state.parsed_resume="{}"
    st.session_state.input_text=""
    st.session_state.job_match="{}"
    st.session_state.job_match_response_id=""
    st.session_state.prev_resp_id=""

if "transcripts" not in st.session_state:
    st.session_state.transcripts = {}  # key -> text we already sent to the API

def step1done():
    #st.session_state.resumeparsed = True
    return


# Initialise
input_text=""
parsed_resume="{}"
prev_resp_id=""
# response2=""
# prev_resp_id2=""

# Configure the web page appearance
st.set_page_config(page_title="Interview App", page_icon="💼")
st.title("Welcome to the Interview App")


if True:
#if not st.session_state.resumeparsed:
    uploaded_file = st.file_uploader('Upload your resume (.pdf format)', type="pdf")
    pasted_resume = st.text_area("Paste your CV:", height=300)

    if uploaded_file is not None:
        uploaded_file.seek(0)  # make sure we start at the beginning
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            input_text = "\n".join(page.get_text("text") for page in doc)
        #df = extract_data(uploaded_file)
    elif pasted_resume.strip():
        input_text=pasted_resume

    # Handle send button click
    #if st.button("📤 Go to Step 2", on_click=step1done) and input_text:
    if st.button("📤 Go to Step 2") and input_text:
        with st.spinner("Parsing your resume..."):
            parsed_resume,prev_resp_id = parse_resume(input_text)
            st.session_state.parsed_resume=parsed_resume
            st.session_state.prev_resp_id=prev_resp_id
            st.session_state.resumeparsed = True
        
        # Display the conversation
        #st.markdown("**You:**")
        #st.write(input_resume)

        #st.markdown("**AI raw:**")
        # st.write(response)

st.markdown("**Resume - JSON for debugging:**")
st.json(st.session_state.parsed_resume, expanded=False)

if True:
#if st.session_state.resumeparsed:
    input_jd=st.text_area("Paste the JD:", height=300)
    if st.button("📤 Generate matches") and input_jd:
        with st.spinner("Finding Job match..."):
            response2, prev_resp_id2 = match_to_jd(input_jd, st.session_state.parsed_resume, st.session_state.prev_resp_id)
            st.session_state.job_match=response2
            st.session_state.job_match_response_id=prev_resp_id2
    
    if st.session_state.job_match and st.session_state.job_match != "{}":
        try:
            feedback_data=json.loads(st.session_state.job_match)
        except json.JSONDecodeError as err:
            st.error(f"Couldn’t parse job match JSON: {err.msg} (line {err.lineno}, col {err.colno})")
        st.subheader("Fit Analysis")
        fit=feedback_data["fit_analysis"]
        st.metric("Tailoring Score", fit["tailoring_score"])
        st.write("Your Strengths:")
        for point in fit["strengths"]:
            st.write(f"- {point}")
        st.write("Your Weaknesses:")
        for point in fit["weaknesses"]:
            st.write(f"- {point}")

        st.subheader("Interview Strategy • Talking Points")
        interview = feedback_data["interview_strategy"]
        for point in interview["talking_points"]:
            st.write(f"- {point['achievement']} ({point['star_competency']})")

        st.subheader("Interview Questions")
        qns = feedback_data["anticipated_questions"]
        for idx, point in enumerate(qns):
            keystr=f"answer_{idx}"
            st.write(f"- [{point['category']}] {point['question']}")
            audio=st.audio_input("Record...", sample_rate=16000, key=keystr)

            if audio and keystr not in st.session_state.transcripts:
                with st.spinner("Transcribing…"):
                    transcript = transcribe_audio(
                        file_bytes=audio.getvalue(),
                        filename=audio.name or f"{keystr}.wav",
                        mime_type=audio.type or "audio/wav",
                    )
                st.session_state.transcripts[keystr] = transcript

            if transcribed_text := st.session_state.transcripts.get(keystr):
                st.write(f"We heard: {transcribed_text}")
                st.write("You can either re-record, or get feedback on this answer")
                with st.expander("Get feedback"):
                    if st.button("🎯Get my feedback") and input_jd:
                        with st.spinner("Evaluating answer..."):
                            response3, prev_resp_id3 = rate_answer(transcribed_text, point['question'], st.session_state.job_match_response_id)
                            st.write(response3)

                            answer_feedback=json.loads(response3)
                            score=answer_feedback["answer_score"]
                            st.subheader(f"Response (score: {score}/10)")
                            for point in answer_feedback["clarity"]:
                                st.write(f"- [Clarity] {point}")
                            for point in answer_feedback["competence"]:
                                st.write(f"- [Competence] {point}")
                            for point in answer_feedback["soft_skills"]:
                                st.write(f"- [Soft Skills] {point}")
                            st.subheader("Suggested Improvements")
                            st.write(answer_feedback["suggested_improvements"])
                            st.subheader("Sample follow-up questions")
                            for point in answer_feedback["follow_up_questions"]:
                                st.write(f"- {point}")
                        
            st.divider()
            

    st.divider()
    st.markdown("**ATS analysis - JSON for debugging:**")
    st.json(st.session_state.job_match, expanded=True)


    
    
    
    
    
# --- Show Latest Commit Message ---
# This snippet displays the last commit message at the bottom-right of the Streamlit app.
# It first checks if a 'commit.txt' file exists (useful for deployments),
# otherwise it falls back to reading the latest commit from git.
# If neither is available, it shows a default message.
# No need to deep dive – just a simple way to know what version of code is running.


import subprocess, os
from pathlib import Path
 
st.markdown(f"<div style='position:fixed; bottom:20px; right:20px; color:gray; font-size:15px; opacity:0.8;'>{(Path(__file__).parent / 'commit.txt').read_text().strip() if (Path(__file__).parent / 'commit.txt').exists() else subprocess.getoutput('git log -1 --pretty=%B') if os.path.exists(Path(__file__).parent / '.git') else 'No commit info'}</div>", unsafe_allow_html=True)
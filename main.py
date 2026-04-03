import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from google.oauth2 import service_account
from text_generator import TextGenerator
from audio_generator import AudioGenerator

# Load environment variables (kept for diagnostic tools only)
load_dotenv()

# Custom CSS for Minimalist Flat Aesthetic
FLAT_CSS = """
<style>
    /* Remove all box-shadows and border-radii */
    * {
        border-radius: 0px !important;
    }
    
    .stButton > button {
        border-radius: 0px !important;
        box-shadow: none !important;
        background-color: #007BFF !important;
        color: white !important;
        border: none !important;
        height: 3rem;
        width: 100%;
        font-weight: bold;
    }

    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 0px !important;
        box-shadow: none !important;
        border: 1px solid #333333 !important;
    }

    /* Minimalist layout padding */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    
    /* Center headings */
    h1, h2, h3 {
        color: #333333;
        text-align: center;
    }
</style>
"""


def run_streamlit_app():
    """Main Streamlit application logic."""
    # --- Sidebar Configuration ---
    st.sidebar.title("☁️ GCP Configuration")
    st.sidebar.info("Please provide your own GCP details to start.")
    
    active_project = st.sidebar.text_input("Project ID", placeholder="my-gcp-project")
    active_location = st.sidebar.text_input("Location (e.g., us-central1)", value="us-central1")
    active_bucket = st.sidebar.text_input("GCS Bucket Name", placeholder="my-audio-bucket")
    custom_key_file = st.sidebar.file_uploader("Upload Service Account JSON", type="json")
    
    active_creds = None
    if custom_key_file:
        try:
            key_dict = json.load(custom_key_file)
            active_creds = service_account.Credentials.from_service_account_info(key_dict)
            st.sidebar.success("✅ Credentials Loaded (In-Memory)")
        except Exception as e:
            st.sidebar.error(f"Error loading JSON: {e}")

    st.title("AU CUSTOMER-AGENT SIMULATOR")
    st.write("---")
    
    # Inputs
    url = st.text_input("Customer Website URL", placeholder="https://www.company.com.au")
    scenario = st.text_area("Conversation Scenario", placeholder="Customer inquiring about a refund status.", height=150)
    
    # Initialise session state for persistence
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'audio_url' not in st.session_state:
        st.session_state.audio_url = None

    # Actions
    if st.button("Generate Script"):
        if not active_creds or not active_project:
            st.warning("Please provide Project ID and Service Account JSON in the sidebar first.")
        elif not url or not scenario:
            st.warning("Please enter both URL and Scenario.")
        else:
            with st.spinner("Generating AU dialogue..."):
                try:
                    tg = TextGenerator(active_project, active_location, credentials=active_creds)
                    st.session_state.transcript = tg.generate_script(url, scenario)
                    # Reset audio when script changes
                    st.session_state.audio_url = None
                except Exception as e:
                    err_msg = str(e)
                    if "API has not been used" in err_msg or "disabled" in err_msg.lower():
                        st.error("Text Generation Failed: Vertex AI API is not enabled.")
                        st.info(f"Enable it here: [Vertex AI API](https://console.cloud.google.com/vertex-ai/publishers?project={active_project})")
                    else:
                        st.error(f"Text Generation Failed: {e}")

    # Transcript Display
    if st.session_state.transcript:
        st.write("### Transcript")
        st.container(border=True).code(st.session_state.transcript, language="markdown")
        
        # Audio Synthesis Action (Visible only after transcript is available)
        st.write("---")
        if st.button("Synthesise Audio"):
            # Deep Validation for Bucket Naming (GCP Constraints)
            is_valid_bucket = bool(re.match(r'^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$', active_bucket)) if active_bucket else False
            
            if not active_creds or not active_project or not active_bucket:
                st.warning("Please provide Project ID, Bucket Name, and JSON Key in the sidebar.")
            elif not is_valid_bucket:
                st.error("Audio Synthesis Failed: Invalid Bucket Name.")
                st.info("Bucket names must start and end with a letter or number, and contain only lowercase letters, numbers, dashes, underscores, and dots (3-63 chars).")
            else:
                with st.spinner("Synthesising Australian audio..."):
                    try:
                        ag = AudioGenerator(active_project, active_bucket, credentials=active_creds)
                        local_path = ag.synthesise_audio(st.session_state.transcript)
                        st.session_state.audio_url = ag.upload_and_sign(local_path)
                    except Exception as e:
                        err_msg = str(e)
                        if "API has not been used" in err_msg or "disabled" in err_msg.lower():
                            st.error("Audio Synthesis Failed: Cloud Text-to-Speech API is not enabled.")
                            st.info(f"Enable it here: [Text-to-Speech API](https://console.developers.google.com/apis/api/texttospeech.googleapis.com/overview?project={active_project})")
                        else:
                            st.error(f"Audio Synthesis Failed: {e}")

    # Audio Display
    if st.session_state.audio_url:
        st.write("### Audio Output")
        st.audio(st.session_state.audio_url)
        
        # Download Button using Signed URL (Styled as per Flat design)
        download_btn_html = f'''
            <a href="{st.session_state.audio_url}" target="_blank" style="text-decoration: none;">
                <div style="
                    background-color: #28a745;
                    color: white;
                    text-align: center;
                    padding: 12px;
                    border: none;
                    text-decoration: none;
                    display: block;
                    font-weight: bold;
                    margin-top: 10px;
                ">
                    DOWNLOAD .WAV FILE
                </div>
            </a>
        '''
        st.markdown(download_btn_html, unsafe_allow_html=True)


def example_customer_simulation():
    """Example method showcasing the functionality as required by rules."""
    print("Starting example AU Customer Simulation...")
    # This is a mock/placeholder to show how logic is called
    # In a real run, this would be triggered by the Streamlit UI
    pass


def main():
    """Entry point for the script."""
    # Showcase functionality via example method
    example_customer_simulation()
    
    # Run the Streamlit app
    run_streamlit_app()


if __name__ == "__main__":
    main()

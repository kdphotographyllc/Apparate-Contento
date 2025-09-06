import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
from prompt import PROMPT_TEMPLATE

# --- Page Configuration ---
st.set_page_config(
    page_title="Gemini Content Generator",
    page_icon="✍️",
    layout="wide"
)

# --- App Title and Description ---
st.title("✍️ Long-Form Content Generator")
st.markdown("This app uses Gemini to generate long-form content based on your detailed content brief. Provide the brief, and the AI will handle the writing. You can then export the result to a Word document.")

# --- API Key Configuration ---
try:
    # Get the API key from Streamlit secrets
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-pro')
except (KeyError, AttributeError):
    st.error("⚠️ Gemini API Key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()


# --- Initialize Session State ---
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""

# --- Main App Interface ---
with st.container(border=True):
    st.subheader("📝 Your Content Brief")
    st.markdown("Provide all the necessary details for the content creation. Include target audience, tone of voice, keywords, desired structure, key points to cover, and what to avoid.")
    
    content_brief = st.text_area(
        "Enter your content brief here:",
        height=300,
        placeholder="E.g., Write a 1500-word blog post about the benefits of remote work for small businesses..."
    )

    generate_button = st.button("🚀 Generate Content", type="primary", use_container_width=True)

if generate_button and content_brief:
    with st.spinner("Generating content... This may take a moment."):
        try:
            # Format the full prompt with the user's brief
            full_prompt = PROMPT_TEMPLATE.format(content_brief=content_brief)
            
            # --- Call Gemini API ---
            response = model.generate_content(full_prompt)
            
            # Store the generated content in session state
            st.session_state.generated_content = response.text
            st.success("Content generated successfully!", icon="✅")

        except Exception as e:
            st.error(f"An error occurred: {e}", icon="🚨")


# --- Display Generated Content and Export Option ---
if st.session_state.generated_content:
    st.markdown("---")
    st.subheader("📄 Generated Content")
    
    with st.container(border=True):
        st.markdown(st.session_state.generated_content)

    # --- Export to .doc ---
    st.markdown("---")
    st.subheader("⬇️ Export Content")
    
    try:
        # Create a document in memory
        document = Document()
        document.add_paragraph(st.session_state.generated_content)
        
        # Save document to a byte stream
        bio = BytesIO()
        document.save(bio)
        
        st.download_button(
            label="Download as .doc file",
            data=bio.getvalue(),
            file_name="generated_content.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"An error occurred during file creation: {e}", icon="🚨")

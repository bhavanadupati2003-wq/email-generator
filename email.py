import streamlit as st
import os
from google import genai
from google.genai import types
import PyPDF2
import io

# Page config
st.set_page_config(
    page_title="Email Generator",
    page_icon="✉️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 14px;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .generated-email {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>✉️ Job Application Email Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Paste a job description, upload your resume, and generate a professional email to recruiters</p>", unsafe_allow_html=True)

st.divider()

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def generate_email(job_description, resume_text, api_key):
    """Generate email using Gemini model"""
    try:
        client = genai.Client(api_key=api_key)
        model = "gemini-2.0-flash"
        
        prompt = f"""You are an expert career coach and professional email writer. Analyze the following job description and resume, then generate a compelling, professional email to send to the recruiter.

**JOB DESCRIPTION:**
{job_description}

**CANDIDATE'S RESUME:**
{resume_text}

**INSTRUCTIONS:**
1. Analyze the job requirements and match them with the candidate's skills and experience
2. Identify the most relevant qualifications and achievements from the resume
3. Generate a professional, concise, and personalized email that:
   - Has an attention-grabbing subject line
   - Opens with enthusiasm for the specific role
   - Highlights 2-3 key qualifications that directly match the job requirements
   - Shows knowledge of the company (if mentioned in JD)
   - Includes a clear call-to-action
   - Maintains a professional yet personable tone
   - Is concise (under 250 words for the body)

**OUTPUT FORMAT:**
**Subject:** [Subject line here]

**Email Body:**
[Email content here]

**Key Matches Found:**
- [Bullet points of how resume matches JD]
"""

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2048,
        )
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        return response.text
        
    except Exception as e:
        st.error(f"Error generating email: {str(e)}")
        return None

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter your Gemini API key",
        help="Get your API key from Google AI Studio"
    )
    
    st.divider()
    
    st.markdown("""
    ### How to use:
    1. Enter your Gemini API key
    2. Paste the job description
    3. Upload your resume (PDF)
    4. Click **Analyze & Generate**
    5. Copy the generated email!
    """)
    
    st.divider()
    
    st.markdown("""
    ### Tips:
    - Use a detailed job description for better results
    - Ensure your resume PDF is text-readable
    - Review and personalize the generated email before sending
    """)

# Main content - Two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=300,
        placeholder="Paste the complete job description including:\n- Job title\n- Company name\n- Requirements\n- Responsibilities\n- Qualifications"
    )

with col2:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=['pdf'],
        help="Upload your resume in PDF format"
    )
    
    if uploaded_file:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Preview option
        with st.expander("Preview extracted text"):
            uploaded_file.seek(0)
            preview_text = extract_text_from_pdf(uploaded_file)
            if preview_text:
                st.text_area("Extracted content", preview_text[:2000] + "..." if len(preview_text) > 2000 else preview_text, height=200)
            uploaded_file.seek(0)

st.divider()

# Generate button
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    generate_btn = st.button(
        "🚀 Analyze & Generate Email",
        type="primary",
        use_container_width=True
    )

# Generate email
if generate_btn:
    # Validation
    if not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar")
    elif not job_description.strip():
        st.error("⚠️ Please paste a job description")
    elif not uploaded_file:
        st.error("⚠️ Please upload your resume PDF")
    else:
        # Extract resume text
        uploaded_file.seek(0)
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if resume_text:
            with st.spinner("🔄 Analyzing job description and resume..."):
                generated_email = generate_email(job_description, resume_text, api_key)
                
            if generated_email:
                st.divider()
                st.subheader("📧 Generated Email")
                
                # Display in a nice container
                st.markdown(f"""<div class='generated-email'>{generated_email}</div>""", unsafe_allow_html=True)
                
                # Also show in copyable text area
                st.text_area(
                    "Copy-friendly version",
                    generated_email,
                    height=400
                )
                
                # Copy button hint
                st.info("💡 Click inside the text area above and press Ctrl+A then Ctrl+C to copy the email")
        else:
            st.error("⚠️ Could not extract text from PDF. Please ensure your PDF contains readable text.")

# Footer
st.divider()
st.markdown("""
<p style='text-align: center; color: #888; font-size: 12px;'>
    Built with Streamlit & Google Gemini | Remember to review and personalize before sending!
</p>
""", unsafe_allow_html=True)
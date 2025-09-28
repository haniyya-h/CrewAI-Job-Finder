import streamlit as st
import os
import json
import requests
import PyPDF2
import io
from fpdf import FPDF
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import tempfile
import base64
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Job Application Crew",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
/* Main container styling */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header styling */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    text-align: center;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.main-header h1 {
    font-size: 3rem;
    margin: 0;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-header p {
    font-size: 1.2rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}

/* Card styling */
.job-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    border-left: 5px solid #667eea;
    transition: all 0.3s ease;
}

.job-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.job-title {
    color: #2c3e50;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.job-company {
    color: #7f8c8d;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.job-location {
    color: #34495e;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.job-description {
    color: #2c3e50;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Form styling */
.form-container {
    background: white;
    border-radius: 15px;
    padding: 2rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.form-title {
    color: #2c3e50;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-align: center;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    cursor: pointer;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* Step indicators */
.step-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 2rem 0;
}

.step {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e0e0e0;
    color: #666;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    margin: 0 10px;
    transition: all 0.3s ease;
}

.step.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.1);
}

.step.completed {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
}

/* Status messages */
.status-success {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    text-align: center;
    font-weight: 600;
}

.status-error {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    text-align: center;
    font-weight: 600;
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2rem;
    }
    
    .job-card {
        padding: 1rem;
    }
    
    .form-container {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

class JobApplicationCrew:
    def __init__(self):
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize agents
        self.job_finder = self._create_job_finder_agent()
        self.resume_tailor = self._create_resume_tailor_agent()
        self.cover_letter_writer = self._create_cover_letter_writer_agent()
        self.reviewer = self._create_reviewer_agent()
        
        # Store application state
        self.job_listings = []
        self.selected_job = None
        self.tailored_resume = ""
        self.cover_letter = ""
        self.reviewed_resume = ""
        self.reviewed_cover_letter = ""
        
    def _create_job_finder_agent(self):
        return Agent(
            role="Job Search Specialist",
            goal="Find relevant job opportunities using the JSearch API",
            backstory="""You are an expert job search specialist with access to the JSearch API. 
            You excel at finding the most relevant job opportunities based on user requirements.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_resume_tailor_agent(self):
        return Agent(
            role="Resume Tailoring Expert",
            goal="Customize resumes to match specific job requirements",
            backstory="""You are a professional resume writer with expertise in tailoring resumes 
            to specific job postings. You understand how to highlight relevant skills and experience.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_cover_letter_writer_agent(self):
        return Agent(
            role="Cover Letter Writer",
            goal="Create compelling, personalized cover letters",
            backstory="""You are an expert cover letter writer who creates personalized, 
            compelling cover letters that connect the candidate's experience to the specific job requirements.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_reviewer_agent(self):
        return Agent(
            role="Document Reviewer",
            goal="Review and improve resumes and cover letters for quality and accuracy",
            backstory="""You are a meticulous document reviewer with expertise in proofreading, 
            grammar checking, and ensuring professional quality in resumes and cover letters.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def search_jobs(self, job_role: str, location: str) -> List[Dict]:
        """Search for jobs using JSearch API"""
        try:
            # Check if API key is available
            api_key = os.getenv("RAPIDAPI_KEY")
            if not api_key:
                logger.error("RAPIDAPI_KEY not found in environment variables")
                return []
            
            # JSearch API endpoint
            url = "https://jsearch.p.rapidapi.com/search"
            
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            params = {
                "query": f"{job_role} in {location}",
                "page": "1",
                "num_pages": "10"
            }
            
            logger.info(f"Searching for jobs: {job_role} in {location}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get("data", [])
            
            # Store job listings
            self.job_listings = jobs
            logger.info(f"Found {len(jobs)} jobs")
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []
    
    def tailor_resume(self, job_description: str, original_resume: str) -> str:
        """Tailor resume to specific job"""
        task = Task(
            description=f"""
            Analyze the job description and tailor the resume to match the requirements.
            
            Job Description:
            {job_description}
            
            Original Resume:
            {original_resume}
            
            Create a tailored resume that:
            1. Highlights relevant skills and experience
            2. Uses keywords from the job description
            3. Maintains professional formatting
            4. Keeps the same structure as the original
            """,
            agent=self.resume_tailor,
            expected_output="A tailored resume text optimized for the specific job"
        )
        
        crew = Crew(
            agents=[self.resume_tailor],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        self.tailored_resume = str(result)
        return self.tailored_resume
    
    def write_cover_letter(self, job_description: str, tailored_resume: str) -> str:
        """Write cover letter for specific job"""
        task = Task(
            description=f"""
            Write a compelling cover letter for this job opportunity.
            
            Job Description:
            {job_description}
            
            Tailored Resume:
            {tailored_resume}
            
            Create a cover letter that:
            1. Addresses the hiring manager professionally
            2. Highlights 2-3 key qualifications
            3. Shows enthusiasm for the role
            4. Includes a strong closing
            5. Is 3-4 paragraphs long
            """,
            agent=self.cover_letter_writer,
            expected_output="A professional cover letter tailored to the job"
        )
        
        crew = Crew(
            agents=[self.cover_letter_writer],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        self.cover_letter = str(result)
        return self.cover_letter
    
    def review_documents(self, resume: str, cover_letter: str) -> tuple:
        """Review and improve both documents"""
        task = Task(
            description=f"""
            Review and improve both the resume and cover letter for:
            1. Grammar and spelling errors
            2. Professional tone and clarity
            3. Consistency in formatting
            4. Overall quality and impact
            
            Resume:
            {resume}
            
            Cover Letter:
            {cover_letter}
            
            Provide improved versions of both documents.
            """,
            agent=self.reviewer,
            expected_output="Improved versions of both resume and cover letter"
        )
        
        crew = Crew(
            agents=[self.reviewer],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # For simplicity, we'll use the result as both documents
        # In a more sophisticated implementation, you'd parse the result
        self.reviewed_resume = str(result)
        self.reviewed_cover_letter = str(result)
        
        return self.reviewed_resume, self.reviewed_cover_letter
    
    def create_pdf(self, content: str, filename: str) -> bytes:
        """Create PDF from text content"""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Split content into lines and add to PDF
            lines = content.split('\n')
            for line in lines:
                # Clean up the line
                line = line.strip()
                if not line:
                    pdf.ln(5)  # Add some space for empty lines
                    continue
                
                # Handle long lines by wrapping
                if len(line) > 80:
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 80:
                            current_line += word + " "
                        else:
                            if current_line:
                                pdf.cell(0, 10, current_line, ln=True)
                            current_line = word + " "
                    if current_line:
                        pdf.cell(0, 10, current_line, ln=True)
                else:
                    pdf.cell(0, 10, line, ln=True)
            
            # Return PDF as bytes
            return pdf.output(dest='S').encode('latin-1')
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def main():
    # Initialize session state
    if 'crew_app' not in st.session_state:
        st.session_state.crew_app = JobApplicationCrew()
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    if 'jobs' not in st.session_state:
        st.session_state.jobs = []
    
    if 'selected_job' not in st.session_state:
        st.session_state.selected_job = None
    
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    
    if 'tailored_resume' not in st.session_state:
        st.session_state.tailored_resume = ""
    
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = ""
    
    if 'reviewed_resume' not in st.session_state:
        st.session_state.reviewed_resume = ""
    
    if 'reviewed_cover_letter' not in st.session_state:
        st.session_state.reviewed_cover_letter = ""
    
    # Beautiful header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Job Application Crew</h1>
        <p>AI-powered job search, resume tailoring, and cover letter generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step indicator
    st.markdown("""
    <div class="step-indicator">
        <div class="step active">1</div>
        <div class="step">2</div>
        <div class="step">3</div>
        <div class="step">4</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Find Jobs", "📝 Tailor Resume", "💌 Cover Letter", "📋 Review & Export"])
    
    with tab1:
        st.markdown('<div class="form-container"><h2 class="form-title">🔍 Search for Job Opportunities</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_role = st.text_input("Job Role/Title", placeholder="e.g., Software Engineer, Data Scientist")
        
        with col2:
            location = st.text_input("Location", placeholder="e.g., New York, Remote")
        
        if st.button("🔍 Search Jobs", type="primary"):
            if job_role and location:
                with st.spinner("Searching for jobs..."):
                    jobs = st.session_state.crew_app.search_jobs(job_role, location)
                    st.session_state.jobs = jobs
                    st.session_state.job_search_completed = True
                
                if jobs:
                    st.success(f"Found {len(jobs)} jobs!")
                else:
                    st.error("No jobs found. Please try different search terms.")
            else:
                st.error("Please enter both job role and location.")
        
        # Display jobs from session state if they exist
        if hasattr(st.session_state, 'jobs') and st.session_state.jobs:
            st.markdown("---")
            st.markdown("### 📋 Available Jobs")
            
            for i, job in enumerate(st.session_state.jobs):
                title = job.get('job_title', 'N/A')
                company = job.get('employer_name', 'N/A')
                city = job.get('job_city', 'N/A')
                state = job.get('job_state', 'N/A')
                location_str = f"{city}, {state}" if city != 'N/A' and state != 'N/A' else (city if city != 'N/A' else 'Location not specified')
                
                description = job.get('job_description', 'No description available')
                if len(description) > 300:
                    description = description[:300] + "..."
                
                job_url = job.get('job_apply_link', '')
                
                st.markdown(f"""
                <div class="job-card">
                    <h3 class="job-title">{title}</h3>
                    <p class="job-company">{company}</p>
                    <p class="job-location">📍 {location_str}</p>
                    <div class="job-description">{description}</div>
                    <p style="margin: 8px 0 0 0;">
                        <a href="{job_url}" target="_blank" class="apply-button" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border-radius: 25px; text-decoration: none; display: inline-block;">Apply Here</a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Job selection button
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"✅ Select This Job", key=f"select_{i}", type="primary"):
                        st.session_state.selected_job = job
                        st.session_state.current_step = 2
                        st.success(f"🎉 Selected: **{title}** at **{company}**")
                        st.info("💡 You can now go to the 'Tailor Resume' tab to customize your resume for this position.")
                        st.rerun()
                
                with col2:
                    if job_url:
                        st.markdown(f'<a href="{job_url}" target="_blank" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 12px 24px; border-radius: 25px; text-decoration: none; display: inline-block;">🔗 Apply Directly</a>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="form-container"><h2 class="form-title">📝 Tailor Your Resume</h2></div>', unsafe_allow_html=True)
        
        if st.session_state.selected_job:
            job_title = st.session_state.selected_job.get('job_title', 'N/A')
            company = st.session_state.selected_job.get('employer_name', 'N/A')
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ Selected Job: **{job_title}** at **{company}**")
            with col2:
                if st.button("🔄 Change Job", help="Select a different job"):
                    st.session_state.selected_job = None
                    st.rerun()
            
            # Debug info
            with st.expander("🔍 Debug: Selected Job Details"):
                st.write("**Job Title:**", job_title)
                st.write("**Company:**", company)
                st.write("**Location:**", f"{st.session_state.selected_job.get('job_city', 'N/A')}, {st.session_state.selected_job.get('job_state', 'N/A')}")
                st.write("**Job Type:**", st.session_state.selected_job.get('job_employment_type', 'N/A'))
                st.write("**Description (first 500 chars):**")
                st.write(st.session_state.selected_job.get('job_description', 'No description available')[:500] + "...")
            
        else:
            st.warning("⚠️ Please select a job first in the 'Find Jobs' tab.")
            st.info("💡 Go to the 'Find Jobs' tab, search for jobs, and click 'Select This Job' on your preferred position.")
        
        # Resume input
        st.subheader("Upload Your Resume")
        
        resume_option = st.radio("Choose input method:", ["Upload PDF", "Paste Text"])
        
        if resume_option == "Upload PDF":
            resume_file = st.file_uploader("Upload PDF Resume", type=['pdf'])
            if resume_file:
                resume_text = extract_text_from_pdf(resume_file)
                st.session_state.resume_text = resume_text
                st.text_area("Extracted Resume Text", value=resume_text, height=200)
        else:
            resume_text = st.text_area("Paste your resume text here:", height=200)
            st.session_state.resume_text = resume_text
        
        if st.button("✂️ Tailor Resume", type="primary"):
            if st.session_state.resume_text and st.session_state.selected_job:
                with st.spinner("Tailoring your resume..."):
                    job_description = st.session_state.selected_job.get('job_description', '')
                    tailored_resume = st.session_state.crew_app.tailor_resume(job_description, st.session_state.resume_text)
                    st.session_state.tailored_resume = tailored_resume
                    st.session_state.current_step = 3
                
                st.success("Resume tailored successfully!")
                st.text_area("Tailored Resume", value=tailored_resume, height=300)
            else:
                st.error("Please provide resume text and select a job first.")
    
    with tab3:
        st.markdown('<div class="form-container"><h2 class="form-title">💌 Generate Cover Letter</h2></div>', unsafe_allow_html=True)
        
        if st.session_state.tailored_resume:
            st.info("Using your tailored resume to generate the cover letter.")
        else:
            st.warning("Please tailor your resume first in the 'Tailor Resume' tab.")
        
        if st.button("✍️ Generate Cover Letter", type="primary"):
            if st.session_state.tailored_resume and st.session_state.selected_job:
                with st.spinner("Generating cover letter..."):
                    job_description = st.session_state.selected_job.get('job_description', '')
                    cover_letter = st.session_state.crew_app.write_cover_letter(job_description, st.session_state.tailored_resume)
                    st.session_state.cover_letter = cover_letter
                    st.session_state.current_step = 4
                
                st.success("Cover letter generated successfully!")
                st.text_area("Cover Letter", value=cover_letter, height=300)
            else:
                st.error("Please tailor your resume first.")
    
    with tab4:
        st.markdown('<div class="form-container"><h2 class="form-title">📋 Review & Export Documents</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Final Resume")
            if st.session_state.tailored_resume:
                st.text_area("Resume", value=st.session_state.tailored_resume, height=200)
                
                if st.button("🔍 Review Resume", type="primary"):
                    with st.spinner("Reviewing resume..."):
                        reviewed_resume, _ = st.session_state.crew_app.review_documents(st.session_state.tailored_resume, st.session_state.cover_letter)
                        st.session_state.reviewed_resume = reviewed_resume
                    st.success("Resume reviewed!")
                    st.text_area("Reviewed Resume", value=reviewed_resume, height=200)
                
                # Download resume PDF
                if st.button("📄 Download Resume PDF"):
                    try:
                        pdf_bytes = st.session_state.crew_app.create_pdf(st.session_state.tailored_resume, "tailored_resume.pdf")
                        st.download_button(
                            label="Download Resume PDF",
                            data=pdf_bytes,
                            file_name="tailored_resume.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error creating PDF: {e}")
            else:
                st.warning("No tailored resume available.")
        
        with col2:
            st.subheader("Final Cover Letter")
            if st.session_state.cover_letter:
                st.text_area("Cover Letter", value=st.session_state.cover_letter, height=200)
                
                if st.button("🔍 Review Cover Letter", type="primary"):
                    with st.spinner("Reviewing cover letter..."):
                        _, reviewed_cover_letter = st.session_state.crew_app.review_documents(st.session_state.tailored_resume, st.session_state.cover_letter)
                        st.session_state.reviewed_cover_letter = reviewed_cover_letter
                    st.success("Cover letter reviewed!")
                    st.text_area("Reviewed Cover Letter", value=reviewed_cover_letter, height=200)
                
                # Download cover letter PDF
                if st.button("📄 Download Cover Letter PDF"):
                    try:
                        pdf_bytes = st.session_state.crew_app.create_pdf(st.session_state.cover_letter, "cover_letter.pdf")
                        st.download_button(
                            label="Download Cover Letter PDF",
                            data=pdf_bytes,
                            file_name="cover_letter.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error creating PDF: {e}")
            else:
                st.warning("No cover letter available.")
    
    # Beautiful footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; margin-top: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
        <h3 style="margin: 0 0 1rem 0;">🎉 Your Job Application Crew is Ready!</h3>
        <p style="margin: 0; opacity: 0.9;">Powered by AI • Built with CrewAI & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Check for required environment variables
    missing_vars = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_vars.append("OPENAI_API_KEY")
        st.error("❌ OPENAI_API_KEY not found in environment variables")
    
    if not os.getenv("RAPIDAPI_KEY"):
        missing_vars.append("RAPIDAPI_KEY")
        st.error("❌ RAPIDAPI_KEY not found in environment variables")
    
    if missing_vars:
        st.error(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        st.info("Please set these variables in your environment or .env file")
    else:
        st.success("✅ All required environment variables are set")
    
    main()

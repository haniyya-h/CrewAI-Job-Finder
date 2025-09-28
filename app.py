import gradio as gr
import os
import sys
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
    
    def create_pdf(self, content: str, filename: str) -> str:
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
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            pdf.output(temp_file.name)
            logger.info(f"PDF created: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            raise

# Initialize the crew
crew_app = JobApplicationCrew()

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

def find_jobs(job_role: str, location: str):
    """Find jobs using the Job Finder agent"""
    if not job_role or not location:
        return "Please enter both job role and location.", []
    
    try:
        jobs = crew_app.search_jobs(job_role, location)
        
        if not jobs:
            return "No jobs found. Please try different search terms.", []
        
        # Format jobs for display as separate cards
        job_cards = []
        for i, job in enumerate(jobs):
            title = job.get('job_title', 'N/A')
            company = job.get('employer_name', 'N/A')
            city = job.get('job_city', 'N/A')
            state = job.get('job_state', 'N/A')
            location = f"{city}, {state}" if city != 'N/A' and state != 'N/A' else (city if city != 'N/A' else 'Location not specified')
            
            description = job.get('job_description', 'No description available')
            # Truncate description if too long
            if len(description) > 300:
                description = description[:300] + "..."
            
            # Get job URL if available
            job_url = job.get('job_apply_link', '')
            apply_text = f"[Apply Here]({job_url})" if job_url else "Apply link not available"
            
            card = f"""
<div class="job-card">
<h3 class="job-title">{title}</h3>
<p class="job-company">{company}</p>
<p class="job-location">📍 {location}</p>
<div class="job-description">
{description}
</div>
<p style="margin: 8px 0 0 0;">
<a href="{job_url}" target="_blank" class="apply-button">{apply_text}</a>
</p>
</div>
"""
            job_cards.append(card)
        
        # Create job selection choices
        job_choices = []
        for i, job in enumerate(jobs):
            title = job.get('job_title', 'N/A')
            company = job.get('employer_name', 'N/A')
            choice_text = f"{title} at {company}"
            job_choices.append((choice_text, i))
        
        return f"Found {len(jobs)} jobs!", job_cards, gr.Dropdown(choices=job_choices, visible=True), gr.Dropdown(choices=job_choices, visible=True)
    
    except Exception as e:
        logger.error(f"Error in find_jobs: {e}")
        return f"Error searching for jobs: {str(e)}", [], gr.Dropdown(choices=[], visible=False), gr.Dropdown(choices=[], visible=False)

def select_job(job_index: int):
    """Select a job from the list"""
    if job_index is not None and job_index < len(crew_app.job_listings):
        crew_app.selected_job = crew_app.job_listings[job_index]
        return f"Selected: {crew_app.selected_job.get('job_title', 'N/A')} at {crew_app.selected_job.get('employer_name', 'N/A')}"
    return "Please select a job first."

def update_job_selection_visibility(job_choices):
    """Update the visibility of job selection elements"""
    if job_choices and len(job_choices) > 0:
        return gr.Dropdown(choices=job_choices, visible=True), gr.Button("Select This Job", variant="secondary", visible=True)
    else:
        return gr.Dropdown(choices=[], visible=False), gr.Button("Select This Job", variant="secondary", visible=False)

def sync_job_choices_to_tailor_tab():
    """Sync job choices to the Tailor Resume tab"""
    if crew_app.job_listings and len(crew_app.job_listings) > 0:
        job_choices = []
        for i, job in enumerate(crew_app.job_listings):
            title = job.get('job_title', 'N/A')
            company = job.get('employer_name', 'N/A')
            choice_text = f"{title} at {company}"
            job_choices.append((choice_text, i))
        
        return gr.Dropdown(choices=job_choices, visible=True), gr.Button("Select This Job", variant="secondary", visible=True)
    else:
        return gr.Dropdown(choices=[], visible=False), gr.Button("Select This Job", variant="secondary", visible=False)

def process_resume(resume_text: str, resume_file):
    """Process uploaded resume (text or PDF)"""
    if resume_file is not None:
        # Extract text from PDF
        text = extract_text_from_pdf(resume_file)
        return text
    return resume_text

def tailor_resume_to_job(resume_text: str):
    """Tailor resume to selected job"""
    try:
        if not crew_app.selected_job:
            return "Please select a job first."
        
        if not resume_text or resume_text.strip() == "":
            return "Please provide your resume text first."
        
        job_description = crew_app.selected_job.get('job_description', '')
        if not job_description:
            return "No job description available for the selected job."
        
        logger.info("Starting resume tailoring...")
        tailored_resume = crew_app.tailor_resume(job_description, resume_text)
        logger.info("Resume tailoring completed")
        return tailored_resume
    
    except Exception as e:
        logger.error(f"Error tailoring resume: {e}")
        return f"Error tailoring resume: {str(e)}"

def generate_cover_letter(tailored_resume: str):
    """Generate cover letter"""
    try:
        if not crew_app.selected_job:
            return "Please select a job first."
        
        if not tailored_resume or tailored_resume.strip() == "":
            return "Please tailor your resume first."
        
        job_description = crew_app.selected_job.get('job_description', '')
        if not job_description:
            return "No job description available for the selected job."
        
        logger.info("Starting cover letter generation...")
        cover_letter = crew_app.write_cover_letter(job_description, tailored_resume)
        logger.info("Cover letter generation completed")
        return cover_letter
    
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return f"Error generating cover letter: {str(e)}"

def review_and_finalize(resume: str, cover_letter: str):
    """Review and finalize documents"""
    try:
        if not resume or resume.strip() == "":
            return "Please provide a resume to review.", "Please provide a resume to review."
        
        if not cover_letter or cover_letter.strip() == "":
            return "Please provide a cover letter to review.", "Please provide a cover letter to review."
        
        logger.info("Starting document review...")
        reviewed_resume, reviewed_cover_letter = crew_app.review_documents(resume, cover_letter)
        logger.info("Document review completed")
        return reviewed_resume, reviewed_cover_letter
    
    except Exception as e:
        logger.error(f"Error reviewing documents: {e}")
        return f"Error reviewing documents: {str(e)}", f"Error reviewing documents: {str(e)}"

def download_resume_pdf(resume_text: str):
    """Create and return PDF of resume"""
    try:
        if not resume_text or resume_text.strip() == "":
            return None
        
        logger.info("Creating resume PDF...")
        pdf_path = crew_app.create_pdf(resume_text, "tailored_resume.pdf")
        logger.info(f"Resume PDF created: {pdf_path}")
        return pdf_path
    
    except Exception as e:
        logger.error(f"Error creating resume PDF: {e}")
        return None

def download_cover_letter_pdf(cover_letter_text: str):
    """Create and return PDF of cover letter"""
    try:
        if not cover_letter_text or cover_letter_text.strip() == "":
            return None
        
        logger.info("Creating cover letter PDF...")
        pdf_path = crew_app.create_pdf(cover_letter_text, "cover_letter.pdf")
        logger.info(f"Cover letter PDF created: {pdf_path}")
        return pdf_path
    
    except Exception as e:
        logger.error(f"Error creating cover letter PDF: {e}")
        return None

# Create Gradio interface
def create_interface():
    # Custom CSS for beautiful styling
    custom_css = """
    <style>
    /* Main container styling */
    .gradio-container {
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
    
    /* Tab styling */
    .tab-nav {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .tab-nav button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        margin: 0 5px;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .tab-nav button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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
    
    .apply-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .apply-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        color: white;
        text-decoration: none;
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
    .primary-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .primary-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .secondary-button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .secondary-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
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
    """
    
    with gr.Blocks(title="Job Application Crew", theme=gr.themes.Soft(), css=custom_css) as app:
        # Beautiful header
        gr.HTML("""
        <div class="main-header">
            <h1>🚀 Job Application Crew</h1>
            <p>AI-powered job search, resume tailoring, and cover letter generation</p>
        </div>
        """)
        
        # Step indicator
        gr.HTML("""
        <div class="step-indicator">
            <div class="step active">1</div>
            <div class="step">2</div>
            <div class="step">3</div>
            <div class="step">4</div>
        </div>
        """)
        
        with gr.Tabs():
            # Tab 1: Find Jobs
            with gr.Tab("🔍 Find Jobs"):
                gr.HTML('<div class="form-container"><h2 class="form-title">🔍 Search for Job Opportunities</h2></div>')
                
                with gr.Row():
                    job_role_input = gr.Textbox(
                        label="Job Role/Title",
                        placeholder="e.g., Software Engineer, Data Scientist",
                        scale=2
                    )
                    location_input = gr.Textbox(
                        label="Location",
                        placeholder="e.g., New York, Remote",
                        scale=1
                    )
                
                search_btn = gr.Button("🔍 Search Jobs", variant="primary", elem_classes=["primary-button"])
                
                search_status = gr.Textbox(label="Search Status", interactive=False)
                job_results = gr.HTML(label="Job Listings")
                
                # Job selection dropdown (hidden initially)
                job_selection = gr.Dropdown(
                    label="Select a Job to Tailor Resume",
                    choices=[],
                    interactive=True,
                    visible=False
                )
                
                # Job selection for Tailor Resume tab
                job_selection_dropdown = gr.Dropdown(
                    label="Select Job from Search Results",
                    choices=[],
                    interactive=True,
                    visible=False
                )
                
                search_btn.click(
                    find_jobs,
                    inputs=[job_role_input, location_input],
                    outputs=[search_status, job_results, job_selection, job_selection_dropdown]
                )
            
            # Tab 2: Tailor Resume
            with gr.Tab("📝 Tailor Resume"):
                gr.HTML('<div class="form-container"><h2 class="form-title">📝 Tailor Your Resume</h2></div>')
                
                # Job selection section
                gr.Markdown("#### Step 1: Select a Job")
                gr.Markdown("**Note:** First search for jobs in the 'Find Jobs' tab, then come back here to select one.")
                
                # Job selection dropdown for Tailor Resume tab
                job_selection_dropdown_tailor = gr.Dropdown(
                    label="Choose a Job from Search Results",
                    choices=[],
                    interactive=True,
                    visible=False
                )
                refresh_jobs_btn = gr.Button("🔄 Refresh Job List", variant="secondary")
                select_job_btn = gr.Button("Select This Job", variant="secondary", visible=False)
                job_selection_status = gr.Textbox(label="Job Selection Status", interactive=False)
                
                # Connect refresh button
                refresh_jobs_btn.click(
                    sync_job_choices_to_tailor_tab,
                    outputs=[job_selection_dropdown_tailor, select_job_btn]
                )
                
                gr.Markdown("#### Step 2: Upload Your Resume")
                with gr.Row():
                    with gr.Column():
                        resume_text_input = gr.Textbox(
                            label="Resume Text",
                            placeholder="Paste your resume text here...",
                            lines=10
                        )
                        resume_file_input = gr.File(
                            label="Or upload PDF resume",
                            file_types=[".pdf"]
                        )
                
                process_resume_btn = gr.Button("📄 Process Resume", variant="primary")
                processed_resume = gr.Textbox(label="Processed Resume", lines=10, interactive=False)
                
                tailor_btn = gr.Button("✂️ Tailor Resume", variant="primary")
                tailored_resume_output = gr.Textbox(label="Tailored Resume", lines=15, interactive=False)
                
                # Connect job selection
                select_job_btn.click(
                    select_job,
                    inputs=[job_selection_dropdown_tailor],
                    outputs=[job_selection_status]
                )
                
                # Connect resume processing
                process_resume_btn.click(
                    process_resume,
                    inputs=[resume_text_input, resume_file_input],
                    outputs=[processed_resume]
                )
                
                # Connect tailoring
                tailor_btn.click(
                    tailor_resume_to_job,
                    inputs=[processed_resume],
                    outputs=[tailored_resume_output]
                )
            
            # Tab 3: Cover Letter
            with gr.Tab("💌 Cover Letter"):
                gr.HTML('<div class="form-container"><h2 class="form-title">💌 Generate Cover Letter</h2></div>')
                
                cover_letter_btn = gr.Button("✍️ Generate Cover Letter", variant="primary")
                cover_letter_output = gr.Textbox(label="Cover Letter", lines=15, interactive=False)
                
                cover_letter_btn.click(
                    generate_cover_letter,
                    inputs=[tailored_resume_output],
                    outputs=[cover_letter_output]
                )
            
            # Tab 4: Review & Export
            with gr.Tab("📋 Review & Export"):
                gr.HTML('<div class="form-container"><h2 class="form-title">📋 Review & Export Documents</h2></div>')
                
                review_btn = gr.Button("🔍 Review Documents", variant="primary")
                
                with gr.Row():
                    with gr.Column():
                        final_resume = gr.Textbox(label="Final Resume", lines=10, interactive=False)
                        download_resume_btn = gr.Button("📄 Download Resume PDF", variant="primary")
                        resume_download = gr.File(label="Resume PDF", visible=False)
                    
                    with gr.Column():
                        final_cover_letter = gr.Textbox(label="Final Cover Letter", lines=10, interactive=False)
                        download_cover_btn = gr.Button("📄 Download Cover Letter PDF", variant="primary")
                        cover_letter_download = gr.File(label="Cover Letter PDF", visible=False)
                
                review_btn.click(
                    review_and_finalize,
                    inputs=[tailored_resume_output, cover_letter_output],
                    outputs=[final_resume, final_cover_letter]
                )
                
                download_resume_btn.click(
                    download_resume_pdf,
                    inputs=[final_resume],
                    outputs=[resume_download]
                )
                
                download_cover_btn.click(
                    download_cover_letter_pdf,
                    inputs=[final_cover_letter],
                    outputs=[cover_letter_download]
                )
        
        # Beautiful footer
        gr.HTML("""
        <div style="text-align: center; padding: 2rem; margin-top: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px;">
            <h3 style="margin: 0 0 1rem 0;">🎉 Your Job Application Crew is Ready!</h3>
            <p style="margin: 0; opacity: 0.9;">Powered by AI • Built with CrewAI & Gradio</p>
        </div>
        """)
    
    return app

if __name__ == "__main__":
    # Check for required environment variables
    missing_vars = []
    
    if not os.getenv("OPENAI_API_KEY"):
        missing_vars.append("OPENAI_API_KEY")
        print("❌ Warning: OPENAI_API_KEY not found in environment variables")
    
    if not os.getenv("RAPIDAPI_KEY"):
        missing_vars.append("RAPIDAPI_KEY")
        print("❌ Warning: RAPIDAPI_KEY not found in environment variables")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the application:")
        for var in missing_vars:
            print(f"  export {var}=your_{var.lower()}")
        print("\nThe application will still start, but some features may not work.")
    else:
        print("✅ All required environment variables are set")
    
    print("\n🚀 Starting Job Application Crew...")
    
    # Create and launch the app
    try:
        app = create_interface()
        app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False
        )
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
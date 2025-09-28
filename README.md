# 🚀 Job Application Crew

An AI-powered job application assistant that helps you find jobs, tailor your resume, and generate personalized cover letters using CrewAI and Streamlit.

## 🌐 Live Demo

**🚀 [Try the Live App](https://crewai-job-finder.streamlit.app/)**

Experience the full functionality of the Job Application Crew with real-time job search, resume tailoring, and cover letter generation.

## ✨ Features

- **🔍 Job Search**: Find relevant job opportunities using JSearch API
- **✂️ Resume Tailoring**: Customize your resume for specific job requirements
- **💌 Cover Letter Generation**: Create personalized cover letters
- **📋 Document Review**: AI-powered review and improvement of documents
- **📄 PDF Export**: Download tailored resumes and cover letters as PDFs
- **🎨 Beautiful UI**: Modern, responsive interface with custom styling

## 🤖 AI Agents

This application uses 4 specialized CrewAI agents:

1. **Job Finder Agent**: Searches for relevant job opportunities
2. **Resume Tailor Agent**: Customizes resumes to match job requirements
3. **Cover Letter Writer Agent**: Creates compelling, personalized cover letters
4. **Reviewer Agent**: Reviews and improves document quality

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd job-application-crew
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

## 🚀 Usage

1. **Run the Streamlit application**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Follow the workflow**:
   - **🔍 Find Jobs**: Search for job opportunities and select your preferred position
   - **📝 Tailor Resume**: Upload your resume (PDF or text) and customize it for the selected job
   - **💌 Cover Letter**: Generate a personalized cover letter based on the job and tailored resume
   - **📋 Review & Export**: Review documents and download PDFs

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- RapidAPI key (for JSearch API)
- Internet connection

## 🔧 API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### RapidAPI Key (JSearch)
1. Go to [RapidAPI](https://rapidapi.com/)
2. Create an account or sign in
3. Search for "JSearch" API
4. Subscribe to the API (free tier available)
5. Copy your API key and add it to your `.env` file

## 📁 Project Structure

```
job-application-crew/
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
├── DEPLOYMENT.md        # Deployment instructions
└── README.md            # This file
```

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud
1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set environment variables in the Streamlit Cloud dashboard
5. Deploy!

### Hugging Face Spaces
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Upload your code
3. Set environment variables in the Space settings
4. Deploy!

## 🎨 Features

- **Modern UI**: Beautiful gradient backgrounds and professional styling
- **Responsive Design**: Works on desktop and mobile devices
- **Session Management**: Data persists across tab switches
- **Debug Information**: Built-in debugging tools for troubleshooting
- **Error Handling**: Comprehensive error handling and user feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

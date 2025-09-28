# 🚀 Job Application Crew

An AI-powered job application assistant that helps you find jobs, tailor your resume, and generate cover letters using CrewAI and advanced AI agents.

![Job Application Crew](https://img.shields.io/badge/AI-Powered-blue) ![Gradio](https://img.shields.io/badge/Interface-Gradio-green) ![CrewAI](https://img.shields.io/badge/Framework-CrewAI-purple)

## ✨ Features

- **🔍 Smart Job Search**: Find relevant job opportunities using JSearch API
- **📝 Resume Tailoring**: AI-powered resume customization for specific jobs
- **💌 Cover Letter Generation**: Create personalized, compelling cover letters
- **📋 Document Review**: AI proofreading and improvement suggestions
- **📄 PDF Export**: Download tailored resumes and cover letters as PDFs
- **🎨 Beautiful UI**: Modern, responsive interface with smooth animations

## 🤖 AI Agents

The application uses 4 specialized AI agents working together:

1. **Job Finder Agent**: Searches for relevant job opportunities
2. **Resume Tailor Agent**: Customizes resumes to match job requirements
3. **Cover Letter Writer Agent**: Creates personalized cover letters
4. **Reviewer Agent**: Proofreads and improves document quality

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- RapidAPI key (for JSearch API)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/job-application-crew.git
   cd job-application-crew
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_openai_api_key_here
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   Open your browser and go to `http://localhost:7860`

## 🎯 How to Use

### Step 1: Find Jobs
- Enter your desired job role and location
- Browse through AI-curated job listings
- Click "Apply Here" buttons to go directly to job applications

### Step 2: Tailor Your Resume
- Upload your resume (text or PDF)
- Select a job from your search results
- Let AI customize your resume for the specific role

### Step 3: Generate Cover Letter
- AI creates a personalized cover letter
- Tailored to the specific job and your background
- Professional tone and compelling content

### Step 4: Review & Export
- Review both documents with AI suggestions
- Download as professional PDFs
- Ready to submit your applications!

## 🌐 Deployment

### Hugging Face Spaces (Recommended)

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Choose Gradio** as the SDK
3. **Connect your GitHub repository**
4. **Set environment variables**:
   - `OPENAI_API_KEY`
   - `RAPIDAPI_KEY`
5. **Deploy automatically!**

Your app will be available at: `https://huggingface.co/spaces/yourusername/job-application-crew`

### Other Deployment Options

- **Railway**: Connect GitHub → Auto-deploy
- **Render**: Connect GitHub → Set environment variables
- **Docker**: Use the included Dockerfile
- **Local**: Run `python app.py` on your server

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `RAPIDAPI_KEY` | Your RapidAPI key for JSearch | Yes |

### API Keys Setup

1. **OpenAI API**: Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **RapidAPI JSearch**: Get your key from [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)

## 📁 Project Structure

```
job-application-crew/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── DEPLOYMENT.md         # Detailed deployment guide
├── .gitignore            # Git ignore rules
└── .env.example          # Environment variables template
```

## 🛠️ Technology Stack

- **Backend**: Python, CrewAI, LangChain
- **Frontend**: Gradio with custom CSS
- **AI**: OpenAI GPT-4o-mini
- **APIs**: JSearch API (RapidAPI)
- **PDF**: fpdf2 for document generation
- **Deployment**: Hugging Face Spaces, Railway, Render

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent framework
- [Gradio](https://gradio.app/) for the beautiful interface
- [OpenAI](https://openai.com/) for the AI capabilities
- [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) for job data

## 📞 Support

If you have any questions or need help:

- 📧 Open an issue on GitHub
- 💬 Join our discussions
- 📖 Check the [deployment guide](DEPLOYMENT.md)

---

**Made with ❤️ by the Job Application Crew team**

*Transform your job search with AI-powered precision!* 🚀
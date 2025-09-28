# 🚀 Deployment Guide for Job Application Crew

This guide covers deployment options for your Job Application Crew Streamlit application.

## 📋 Prerequisites

- Your application files: `streamlit_app.py`, `requirements.txt`, `README.md`
- API Keys: OpenAI API key and RapidAPI key
- GitHub account

---

## ☁️ Option 1: Streamlit Cloud (Recommended)

**Best for:** Free hosting, easy setup, automatic deployments from GitHub

### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/job-application-crew.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Fill in the details:
     - **Repository**: `yourusername/job-application-crew`
     - **Branch**: `main`
     - **Main file path**: `streamlit_app.py`
     - **App URL**: `job-application-crew` (optional)

3. **Set Environment Variables**
   - In the Streamlit Cloud dashboard, go to "Settings"
   - Add these secrets:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `RAPIDAPI_KEY`: Your RapidAPI key

4. **Deploy**
   - Click "Deploy!"
   - Your app will be available at: `https://job-application-crew.streamlit.app`

### Benefits:
- ✅ Free hosting
- ✅ Automatic deployments from GitHub
- ✅ Easy environment variable management
- ✅ Built-in analytics
- ✅ Custom domains (Pro plan)

---

## 🏠 Option 2: Local Development

**Best for:** Development and testing

### Steps:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

3. **Run the Application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the App**
   - Open your browser to `http://localhost:8501`

---

## 🐳 Option 3: Docker (Advanced)

**Best for:** Production deployments, custom infrastructure

### Steps:

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t job-application-crew .
   docker run -p 8501:8501 -e OPENAI_API_KEY=your_key -e RAPIDAPI_KEY=your_key job-application-crew
   ```

---

## 🔧 Environment Variables

### Required Variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `RAPIDAPI_KEY`: Your RapidAPI key for JSearch API

### Getting API Keys:

#### OpenAI API Key:
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

#### RapidAPI Key (JSearch):
1. Go to [RapidAPI](https://rapidapi.com/)
2. Create an account or sign in
3. Search for "JSearch" API
4. Subscribe to the API (free tier available)
5. Copy your API key

---

## 🚀 Quick Start (Streamlit Cloud)

1. **Fork this repository** or create your own
2. **Push to GitHub** with your code
3. **Go to [share.streamlit.io](https://share.streamlit.io)**
4. **Connect your GitHub repository**
5. **Set environment variables** in Streamlit Cloud settings
6. **Deploy!**

Your app will be live at: `https://your-app-name.streamlit.app`

---

## 📊 Monitoring and Analytics

### Streamlit Cloud Features:
- **Usage Analytics**: Track app usage and performance
- **Error Logs**: Monitor errors and debug issues
- **Custom Domains**: Use your own domain (Pro plan)
- **Team Collaboration**: Share apps with team members

### Local Development:
- **Debug Mode**: Use `streamlit run streamlit_app.py --logger.level debug`
- **Hot Reload**: Automatic reload on file changes
- **Browser DevTools**: Use browser developer tools for debugging

---

## 🔒 Security Best Practices

1. **Never commit API keys** to your repository
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Regular updates** of dependencies
5. **Monitor usage** and set API limits

---

## 🆘 Troubleshooting

### Common Issues:

1. **App won't start**
   - Check environment variables are set
   - Verify all dependencies are installed
   - Check the logs in Streamlit Cloud dashboard

2. **API errors**
   - Verify API keys are correct
   - Check API quotas and limits
   - Ensure internet connectivity

3. **Import errors**
   - Check `requirements.txt` includes all dependencies
   - Verify Python version compatibility

### Getting Help:
- Check [Streamlit Documentation](https://docs.streamlit.io/)
- Visit [Streamlit Community](https://discuss.streamlit.io/)
- Review error logs in Streamlit Cloud dashboard

---

## 📈 Scaling and Performance

### Streamlit Cloud Limits:
- **Free tier**: 1 app, basic features
- **Pro tier**: Multiple apps, advanced features, custom domains
- **Enterprise**: Custom solutions for large organizations

### Performance Tips:
- **Optimize imports**: Only import what you need
- **Use caching**: Leverage `@st.cache_data` for expensive operations
- **Limit data**: Don't load unnecessary data
- **Monitor memory**: Watch for memory leaks

---

## 🎉 Success!

Once deployed, your Job Application Crew will be available to users worldwide. The app provides:

- **Job Search**: Find relevant opportunities
- **Resume Tailoring**: Customize resumes for specific jobs
- **Cover Letter Generation**: Create personalized cover letters
- **PDF Export**: Download professional documents

Happy deploying! 🚀
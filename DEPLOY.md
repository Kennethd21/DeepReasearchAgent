# Deployment Guide

## Option 1: Streamlit Community Cloud (Recommended)

### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `src/ui/streamlit_app.py`
   - Click "Deploy!"

3. **Add Secrets**
   - In Streamlit Cloud dashboard, go to app settings
   - Add secrets:
     ```
     GEMINI_API_KEY = "your_key_here"
     TAVILY_API_KEY = "your_key_here"
     ```

### Troubleshooting

**Issue: ModuleNotFoundError**
- Ensure `requirements.txt` is in root directory
- Check that all dependencies are listed

**Issue: Secrets not found**
- Secrets must be added in Streamlit Cloud dashboard
- Not in .env file for deployed apps

## Option 2: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init

# Set environment variables
railway variables set GEMINI_API_KEY=your_key
railway variables set TAVILY_API_KEY=your_key

# Deploy
railway up
```

## Option 3: Render

1. Connect GitHub repo
2. Create new Web Service
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run src/ui/streamlit_app.py --server.port $PORT`
5. Add environment variables in dashboard

## Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| GEMINI_API_KEY | Google AI Studio API key | [aistudio.google.com](https://aistudio.google.com) |
| TAVILY_API_KEY | Tavily search API key | [tavily.com](https://tavily.com) |

## Local Testing

Before deploying, test locally:
```bash
cp .env.example .env
# Add your keys to .env
streamlit run src/ui/streamlit_app.py
```

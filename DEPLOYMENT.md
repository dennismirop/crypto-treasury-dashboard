# Deployment Guide

This guide will help you deploy the Crypto Treasury Expansions Dashboard to GitHub and Streamlit Cloud.

## GitHub Deployment

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right and select "New repository"
3. Name your repository (e.g., `crypto-treasury-dashboard`)
4. Make it public or private as preferred
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### 2. Push to GitHub

```bash
# Add all files to git
git add .

# Commit the changes
git commit -m "Initial commit: Crypto Treasury Dashboard with Flask and Streamlit"

# Add the remote repository (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/crypto-treasury-dashboard.git

# Push to GitHub
git push -u origin main
```

## Streamlit Cloud Deployment

### 1. Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `crypto-treasury-dashboard`
5. Set the main file path: `streamlit_app.py`
6. Set the Python version: `3.9` or higher
7. Click "Deploy!"

### 2. Configuration

The app will automatically use the configuration from `.streamlit/config.toml`.

### 3. Environment Variables (Optional)

If you need to set environment variables:
1. Go to your app settings in Streamlit Cloud
2. Add any required environment variables
3. Redeploy the app

## Local Development

### Flask Version
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py

# Access at http://localhost:5005
```

### Streamlit Version
```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Access at http://localhost:8501
```

## File Structure for Deployment

```
crypto-treasury-dashboard/
├── app.py                    # Flask web application
├── streamlit_app.py          # Streamlit web application
├── crypto_scraper.py         # News scraping logic
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── DEPLOYMENT.md            # This deployment guide
├── .gitignore               # Git ignore rules
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── templates/
│   └── index.html           # Flask dashboard template
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── dashboard.js     # Dashboard JavaScript
└── crypto_treasury_news.json # Generated news data (ignored by git)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Port Conflicts**: The Flask app runs on port 5005, Streamlit on 8501
3. **Data File**: The `crypto_treasury_news.json` file is ignored by git and will be generated on first run

### Streamlit Cloud Issues

1. **Deployment Fails**: Check the logs in Streamlit Cloud for error messages
2. **Missing Dependencies**: Ensure all packages are in `requirements.txt`
3. **File Not Found**: Make sure `streamlit_app.py` is in the root directory

### GitHub Issues

1. **Large Files**: The `crypto_treasury_news.json` file is ignored by git
2. **Authentication**: Use GitHub CLI or SSH keys for authentication
3. **Branch Issues**: Make sure you're on the `main` branch

## Maintenance

### Updating the App

1. Make your changes locally
2. Test both Flask and Streamlit versions
3. Commit and push to GitHub
4. Streamlit Cloud will automatically redeploy

### Monitoring

- Check Streamlit Cloud logs for any errors
- Monitor the app performance
- Update dependencies as needed

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the logs in Streamlit Cloud
3. Ensure all dependencies are properly installed
4. Verify your internet connection for news scraping 
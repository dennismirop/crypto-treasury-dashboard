# Crypto Treasury Expansions Dashboard

A real-time web dashboard that monitors and displays cryptocurrency treasury expansions, acquisitions, and new announcements from Google News RSS feeds. The application automatically scrapes news from the last 24 hours and filters specifically for treasury expansion activities and fresh announcements.

## Features

- 🔍 **Real-time Expansion Tracking**: Automatically fetches crypto treasury expansion news from Google News RSS feeds
- ⏰ **24-Hour Filter**: Only displays news from the last 24 hours
- 🎯 **Expansion Focus**: Filters news specifically for treasury expansions, acquisitions, and new announcements
- 📊 **Interactive Dashboard**: Modern, responsive web interface with statistics
- 🔄 **Auto-refresh**: Automatically updates every 30 minutes
- 🎛️ **Smart Filtering**: Filter by all articles, expansions & announcements, or new announcements only
- 📱 **Mobile Responsive**: Works seamlessly on desktop and mobile devices
- 📈 **Analytics**: Shows top news sources and search queries
- 🎨 **Modern UI**: Beautiful, user-friendly interface with Bootstrap 5

## Screenshots

The dashboard features:
- Header with real-time update status
- Statistics cards showing total articles, sources, and queries
- Main news feed with article details
- Sidebar with top sources and search queries
- Responsive design for all devices

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   cd crypto-news-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the dashboard**
   Open your web browser and navigate to: `http://localhost:5005`

## Usage

### Starting the Application

```bash
python app.py
```

The application will:
- Start the Flask web server on port 5000
- Begin background scraping of crypto treasury news
- Automatically refresh news every 30 minutes
- Save news data to `crypto_treasury_news.json`

### Manual Refresh

- Click the "Refresh News" button in the dashboard to manually update the news feed
- The scraper will fetch the latest news from Google News RSS feeds

### Filtering Articles

The dashboard includes three filter options:
- **All Articles**: Shows all treasury-related articles
- **Expansions & Announcements**: Shows only expansion and new announcement articles
- **New Announcements Only**: Shows only new strategic announcements

### API Endpoints

- `GET /` - Main dashboard page
- `GET /api/news` - Get latest news data
- `GET /api/refresh` - Manually refresh news
- `GET /api/stats` - Get dashboard statistics

## How It Works

### News Scraping

The application uses multiple search queries to find crypto treasury expansion news:

- "crypto treasury expansion"
- "bitcoin treasury acquisition"
- "ethereum treasury purchase"
- "cryptocurrency treasury announcement"
- "crypto company adds bitcoin"
- "blockchain treasury investment"
- "defi treasury launch"
- "crypto balance sheet expansion"
- "digital asset treasury acquisition"
- "crypto investment announcement"
- "bitcoin treasury reserves increase"
- "ethereum holdings expansion"
- "crypto company buys bitcoin"
- "treasury bitcoin acquisition"
- "crypto reserves announcement"

### Filtering Logic

Articles are filtered based on:
1. **Crypto Keywords**: bitcoin, ethereum, crypto, cryptocurrency, blockchain, etc.
2. **Treasury Keywords**: treasury, reserves, holdings, balance sheet, cash reserves, etc.
3. **Expansion Keywords**: expands, acquires, adds, announces, launches, increases, etc.
4. **Time Filter**: Only articles from the last 24 hours

### Data Storage

News data is stored in `crypto_treasury_news.json` with the following structure:
```json
{
  "last_updated": "2024-01-01T12:00:00",
  "articles": [
    {
      "title": "Article Title",
      "description": "Article description",
      "link": "https://article-url.com",
      "published": "2024-01-01T10:00:00",
      "source": "News Source",
      "query": "Search query used"
    }
  ]
}
```

## Project Structure

```
crypto-news-dashboard/
├── app.py                 # Flask web application
├── crypto_scraper.py      # News scraping logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main dashboard template
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── dashboard.js  # Dashboard JavaScript
└── crypto_treasury_news.json  # Generated news data
```

## Configuration

### Customizing Search Queries

Edit the `queries` list in `crypto_scraper.py` to add or modify search terms:

```python
queries = [
    "crypto treasury reserves",
    "bitcoin treasury holdings",
    # Add your custom queries here
]
```

### Adjusting Update Frequency

Modify the background scraper interval in `app.py`:

```python
# Change from 1800 seconds (30 minutes) to your preferred interval
time.sleep(1800)
```

### Changing Keywords

Update the keyword lists in `crypto_scraper.py`:

```python
self.treasury_keywords = [
    "treasury", "reserves", "holdings",
    # Add more treasury-related keywords
]

self.crypto_keywords = [
    "bitcoin", "ethereum", "crypto",
    # Add more crypto-related keywords
]
```

## Troubleshooting

### Common Issues

1. **No news articles found**
   - Check your internet connection
   - Verify that Google News RSS feeds are accessible
   - Try refreshing manually

2. **Application won't start**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check if port 5000 is available
   - Verify Python version (3.8+)

3. **Slow loading**
   - The initial scrape may take a few minutes
   - Subsequent updates are faster
   - Check your internet connection

### Logs

The application logs information to the console. Look for:
- Scraping progress messages
- Error messages for failed requests
- Success messages for completed operations

## Contributing

Feel free to contribute to this project by:
- Adding new search queries
- Improving the filtering logic
- Enhancing the UI/UX
- Adding new features
- Fixing bugs

## License

This project is open source and available under the MIT License.

## Disclaimer

This application is for educational and informational purposes only. The news content is sourced from Google News RSS feeds and is subject to their terms of service. Always verify information from multiple sources before making any financial decisions.

## Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Review the console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify your internet connection

---

**Built with ❤️ using Python, Flask, and modern web technologies** 
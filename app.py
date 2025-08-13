from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from crypto_scraper import CryptoNewsScraper
import json
import os
from datetime import datetime
import threading
import time
import schedule

app = Flask(__name__)
CORS(app)

# Global scraper instance
scraper = CryptoNewsScraper()
last_update_time = None

def background_scraper():
    """Background task to run the scraper periodically"""
    global last_update_time
    while True:
        try:
            print("Running background scraper...")
            scraper.scrape_all_crypto_treasury_news()
            scraper.save_to_json()
            last_update_time = datetime.now()
            print(f"Scraper completed at {last_update_time}")
        except Exception as e:
            print(f"Error in background scraper: {e}")
        
        # Wait for 30 minutes before next run
        time.sleep(1800)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    """API endpoint to get latest news"""
    try:
        # Try to load from file first
        if os.path.exists('crypto_treasury_news.json'):
            with open('crypto_treasury_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data)
        else:
            # If no file exists, run scraper once
            articles = scraper.scrape_all_crypto_treasury_news()
            scraper.save_to_json()
            return jsonify({
                'last_updated': datetime.now().isoformat(),
                'articles': articles
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['GET', 'POST'])
def refresh_news():
    """API endpoint to manually refresh news"""
    try:
        articles = scraper.scrape_all_crypto_treasury_news()
        scraper.save_to_json()
        return jsonify({
            'last_updated': datetime.now().isoformat(),
            'articles': articles,
            'message': 'News refreshed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get dashboard statistics"""
    try:
        if os.path.exists('crypto_treasury_news.json'):
            with open('crypto_treasury_news.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                articles = data.get('articles', [])
                
                # Calculate statistics
                total_articles = len(articles)
                sources = {}
                queries = {}
                
                for article in articles:
                    source = article.get('source', 'Unknown')
                    query = article.get('query', 'Unknown')
                    
                    sources[source] = sources.get(source, 0) + 1
                    queries[query] = queries.get(query, 0) + 1
                
                return jsonify({
                    'total_articles': total_articles,
                    'top_sources': dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]),
                    'top_queries': dict(sorted(queries.items(), key=lambda x: x[1], reverse=True)[:5]),
                    'last_updated': data.get('last_updated')
                })
        else:
            return jsonify({
                'total_articles': 0,
                'top_sources': {},
                'top_queries': {},
                'last_updated': None
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start background scraper in a separate thread
    scraper_thread = threading.Thread(target=background_scraper, daemon=True)
    scraper_thread.start()
    
    # Run initial scrape
    try:
        scraper.scrape_all_crypto_treasury_news()
        scraper.save_to_json()
        last_update_time = datetime.now()
    except Exception as e:
        print(f"Initial scrape failed: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5006) 
import streamlit as st
import json
import os
from datetime import datetime
import requests
from crypto_scraper import CryptoNewsScraper
import time

# Page configuration
st.set_page_config(
    page_title="Crypto Treasury Announcements Dashboard",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean, professional design
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .article-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .article-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .badge {
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-announcement { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
    }
    
    .badge-expansion { 
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white; 
    }
    
    .badge-activity { 
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white; 
    }
    
    .article-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .article-title a {
        color: #1f2937;
        text-decoration: none;
    }
    
    .article-title a:hover {
        color: #667eea;
    }
    
    .article-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 1rem;
        padding-top: 0.5rem;
        border-top: 1px solid #f3f4f6;
    }
    
    .refresh-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    
    .refresh-button:hover {
        transform: translateY(-1px);
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stSidebar {display: none;}
</style>
""", unsafe_allow_html=True)

# Initialize scraper
@st.cache_resource
def get_scraper():
    return CryptoNewsScraper()

scraper = get_scraper()

# Load news data
def load_news_data():
    if os.path.exists('crypto_treasury_news.json'):
        with open('crypto_treasury_news.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'articles': [], 'last_updated': None}

# Get article type with focus on announcements
def get_article_type(article):
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    
    # Primary announcement keywords (highest priority)
    primary_announcement = [
        'announces', 'announced', 'announcement', 'launches', 'launched', 'launch',
        'reveals', 'revealed', 'reveal', 'unveils', 'unveiled', 'unveil',
        'introduces', 'introduced', 'starts', 'started', 'begins', 'began'
    ]
    
    # Secondary announcement keywords
    secondary_announcement = [
        'new', 'fresh', 'latest', 'recent', 'strategic', 'initiative', 'program'
    ]
    
    # Expansion keywords
    expansion_keywords = [
        'buys', 'bought', 'purchases', 'purchased', 'acquires', 'acquired', 
        'adds', 'added', 'expands', 'expanded', 'increases', 'increased'
    ]
    
    # Check for primary announcement keywords first
    has_primary_announcement = any(keyword in text for keyword in primary_announcement)
    has_secondary_announcement = any(keyword in text for keyword in secondary_announcement)
    has_expansion = any(keyword in text for keyword in expansion_keywords)
    
    # Prioritize announcements
    if has_primary_announcement:
        return 'New Announcement'
    elif has_primary_announcement and has_expansion:
        return 'New Announcement'
    elif has_expansion:
        return 'Expansion'
    elif has_secondary_announcement:
        return 'Treasury Activity'
    else:
        return 'Treasury Activity'

# Filter articles to focus on new announcements
def filter_articles(articles, filter_type):
    if filter_type == 'all':
        return articles
    
    filtered = []
    for article in articles:
        article_type = get_article_type(article)
        
        if filter_type == 'announcements':
            # Only show new announcements
            if article_type == 'New Announcement':
                filtered.append(article)
        elif filter_type == 'expansions':
            # Show announcements and expansions
            if article_type in ['New Announcement', 'Expansion']:
                filtered.append(article)
    
    return filtered

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📢 Crypto Treasury Announcements Dashboard</h1>
        <p>Real-time monitoring of NEW cryptocurrency treasury announcements, strategic initiatives, and corporate crypto adoption</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter options in main area
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        filter_type = st.radio(
            "Filter Articles:",
            options=['all', 'announcements', 'expansions'],
            format_func=lambda x: {
                'all': '📰 All Articles',
                'announcements': '📢 New Announcements Only',
                'expansions': '📈 Announcements & Expansions'
            }[x],
            horizontal=True
        )
    
    with col2:
        st.write("")  # Spacer
    
    with col3:
        if st.button("🔄 Refresh News", type="primary", use_container_width=True):
            with st.spinner("Refreshing news data..."):
                try:
                    articles = scraper.scrape_all_crypto_treasury_news()
                    scraper.save_to_json()
                    st.success("News refreshed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error refreshing news: {e}")
    
    # Load data
    data = load_news_data()
    articles = data.get('articles', [])
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Total Articles</h3>
            <h2>{len(articles)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sources = set(article.get('source', 'Unknown') for article in articles)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📰 News Sources</h3>
            <h2>{len(sources)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Count new announcements
        new_announcements = sum(1 for article in articles if get_article_type(article) == 'New Announcement')
        st.markdown(f"""
        <div class="metric-card">
            <h3>📢 New Announcements</h3>
            <h2>{new_announcements}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        last_updated = data.get('last_updated')
        if last_updated:
            try:
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                time_ago = datetime.now() - dt.replace(tzinfo=None)
                minutes_ago = int(time_ago.total_seconds() / 60)
                if minutes_ago < 60:
                    time_str = f"{minutes_ago}m ago"
                else:
                    hours_ago = minutes_ago // 60
                    time_str = f"{hours_ago}h ago"
            except:
                time_str = "Unknown"
        else:
            time_str = "Never"
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏰ Last Updated</h3>
            <h2>{time_str}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter articles
    filtered_articles = filter_articles(articles, filter_type)
    
    # Articles section
    st.markdown(f"## 📰 Latest Treasury Announcements ({len(filtered_articles)} of {len(articles)})")
    
    if not filtered_articles:
        st.info("No articles match the current filter. Try selecting a different filter option or refresh the news.")
    else:
        for article in filtered_articles:
            article_type = get_article_type(article)
            
            # Determine badge class
            if article_type == 'New Announcement':
                badge_class = 'badge-announcement'
            elif article_type == 'Expansion':
                badge_class = 'badge-expansion'
            else:
                badge_class = 'badge-activity'
            
            # Format date
            try:
                pub_date = datetime.fromisoformat(article.get('published', '').replace('Z', '+00:00'))
                formatted_date = pub_date.strftime('%b %d, %H:%M')
            except:
                formatted_date = "Unknown"
            
            st.markdown(f"""
            <div class="article-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 class="article-title">
                        <a href="{article.get('link', '#')}" target="_blank">
                            {article.get('title', 'No title')}
                        </a>
                    </h4>
                    <span class="badge {badge_class}">{article_type}</span>
                </div>
                <p style="color: #6b7280; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.5;">
                    {article.get('description', 'No description')[:250]}...
                </p>
                <div class="article-meta">
                    <span>📅 {formatted_date}</span>
                    <span>📰 {article.get('source', 'Unknown')}</span>
                    <span>🔍 {article.get('query', 'Unknown')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
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
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #6366f1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .article-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .badge-expansion { background-color: #10b981; color: white; }
    .badge-announcement { background-color: #3b82f6; color: white; }
    .badge-activity { background-color: #6b7280; color: white; }
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

# Get article type
def get_article_type(article):
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    
    primary_expansion = ['buys', 'bought', 'purchases', 'purchased', 'acquires', 'acquired', 'adds', 'added']
    primary_announcement = ['announces', 'announced', 'launches', 'launched', 'reveals', 'revealed']
    
    has_primary_expansion = any(keyword in text for keyword in primary_expansion)
    has_primary_announcement = any(keyword in text for keyword in primary_announcement)
    
    if has_primary_expansion and has_primary_announcement:
        return 'Expansion & Announcement'
    elif has_primary_expansion:
        return 'Expansion'
    elif has_primary_announcement:
        return 'New Announcement'
    else:
        return 'Treasury Activity'

# Filter articles
def filter_articles(articles, filter_type):
    if filter_type == 'all':
        return articles
    
    filtered = []
    for article in articles:
        article_type = get_article_type(article)
        
        if filter_type == 'expansions':
            if article_type in ['Expansion', 'New Announcement', 'Expansion & Announcement']:
                filtered.append(article)
        elif filter_type == 'announcements':
            if article_type in ['New Announcement', 'Expansion & Announcement']:
                filtered.append(article)
    
    return filtered

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📢 Crypto Treasury Announcements Dashboard</h1>
        <p>Real-time monitoring of NEW cryptocurrency treasury announcements, acquisitions, and strategic initiatives</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Filters & Controls")
    
    # Filter options
    filter_type = st.sidebar.radio(
        "Filter Articles:",
        options=['all', 'expansions', 'announcements'],
        format_func=lambda x: {
            'all': '📰 All Articles',
            'expansions': '📢 New Announcements',
            'announcements': '📢 New Announcements Only'
        }[x]
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh News", type="primary"):
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
        queries = set(article.get('query', 'Unknown') for article in articles)
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔍 Search Queries</h3>
            <h2>{len(queries)}</h2>
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
    st.markdown(f"## 📰 Articles ({len(filtered_articles)} of {len(articles)})")
    
    if not filtered_articles:
        st.info("No articles match the current filter. Try selecting a different filter option.")
    else:
        for article in filtered_articles:
            article_type = get_article_type(article)
            
            # Determine badge class
            if 'Expansion' in article_type:
                badge_class = 'badge-expansion'
            elif 'Announcement' in article_type:
                badge_class = 'badge-announcement'
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
                    <h4 style="margin: 0; flex: 1;">
                        <a href="{article.get('link', '#')}" target="_blank" style="text-decoration: none; color: #1f2937;">
                            {article.get('title', 'No title')}
                        </a>
                    </h4>
                    <span class="badge {badge_class}">{article_type}</span>
                </div>
                <p style="color: #6b7280; margin: 0.5rem 0; font-size: 0.9rem;">
                    {article.get('description', 'No description')[:200]}...
                </p>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #9ca3af;">
                    <span>📅 {formatted_date}</span>
                    <span>📰 {article.get('source', 'Unknown')}</span>
                    <span>🔍 {article.get('query', 'Unknown')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Sidebar analytics
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Analytics")
    
    # Top sources
    if articles:
        source_counts = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        st.sidebar.markdown("### Top Sources")
        for source, count in top_sources:
            st.sidebar.markdown(f"**{source}**: {count}")
    
    # Top queries
    if articles:
        query_counts = {}
        for article in articles:
            query = article.get('query', 'Unknown')
            query_counts[query] = query_counts.get(query, 0) + 1
        
        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        st.sidebar.markdown("### Top Queries")
        for query, count in top_queries:
            st.sidebar.markdown(f"**{query}**: {count}")

if __name__ == "__main__":
    main() 
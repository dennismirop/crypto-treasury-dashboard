import xmltodict
import requests
from datetime import datetime, timedelta
import json
import time
import re
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoNewsScraper:
    def __init__(self):
        self.base_url = "https://news.google.com/rss"
        # Keywords for treasury expansions and new announcements
        self.expansion_keywords = [
            "expands", "expanded", "expansion", "increases", "increased", "increase",
            "adds", "added", "addition", "acquires", "acquired", "acquisition",
            "buys", "bought", "purchases", "purchased", "purchase",
            "announces", "announced", "announcement", "launches", "launched", "launch",
            "reveals", "revealed", "reveal", "unveils", "unveiled", "unveil",
            "new", "fresh", "latest", "recent", "updates", "updated",
            "boosts", "boosted", "boost", "grows", "grew", "growth",
            "strategic", "investment", "portfolio", "holdings", "reserves"
        ]
        # Keywords for treasury-related terms
        self.treasury_keywords = [
            "treasury", "reserves", "holdings", "balance sheet", "cash reserves",
            "treasury management", "treasury operations", "treasury department",
            "financial reserves", "asset management", "portfolio management",
            "investment strategy", "treasury bonds", "treasury bills",
            "treasury securities", "treasury yield", "treasury curve",
            "corporate treasury", "company treasury", "institutional holdings"
        ]
        self.crypto_keywords = [
            "bitcoin", "ethereum", "solana", "cardano", "polkadot", "chainlink", "avalanche", "polygon",
            "crypto", "cryptocurrency", "blockchain", "defi", "nft", "web3", "digital assets",
            "btc", "eth", "sol", "ada", "dot", "link", "avax", "matic",
            "stablecoin", "altcoin", "token", "coin", "mining", "staking",
            "binance coin", "bnb", "ripple", "xrp", "litecoin", "ltc", "dogecoin", "doge",
            "uniswap", "uni", "aave", "compound", "maker", "mkr", "sushi", "sushi"
        ]
        self.news_data = []
        
    def get_google_news_rss_url(self, query: str) -> str:
        """Generate Google News RSS URL for a specific query"""
        encoded_query = requests.utils.quote(query)
        return f"{self.base_url}/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    def is_treasury_expansion(self, title: str, description: str) -> bool:
        """Check if the news article is about specific company treasury expansions or announcements"""
        text = f"{title} {description}".lower()
        
        # Must contain at least one crypto keyword
        has_crypto = any(keyword in text for keyword in self.crypto_keywords)
        if not has_crypto:
            return False
            
        # Must contain at least one treasury keyword
        has_treasury = any(keyword in text for keyword in self.treasury_keywords)
        if not has_treasury:
            return False
            
        # Must contain at least one expansion/announcement keyword
        has_expansion = any(keyword in text for keyword in self.expansion_keywords)
        if not has_expansion:
            return False
            
        # EXCLUDE general market news patterns
        exclude_patterns = [
            "collectively increased", "collectively added", "collectively grew", "collectively expanded",
            "entities collectively", "treasury entities", "bitcoin entities", "crypto entities",
            "were added", "was added", "have been added", "has been added",
            "market analysis", "market commentary", "market overview", "market report",
            "sector analysis", "industry analysis", "market trend", "market movement",
            "price analysis", "price movement", "price trend", "technical analysis",
            "fundamental analysis", "trading volume", "trading activity"
        ]
        
        # Reject if it contains general market language
        if any(pattern in text for pattern in exclude_patterns):
            return False
            
        # Must contain specific company action patterns
        company_action_patterns = [
            r'\b(announces|announced)\s+(?:that\s+)?(?:it\s+)?(?:has\s+)?(?:will\s+)?(?:plans\s+to\s+)?(?:to\s+)?(?:add|acquire|buy|purchase|expand|increase)',
            r'\b(adds|added|acquires|acquired|buys|bought|purchases|purchased)\s+(?:an?\s+)?(?:additional\s+)?(?:more\s+)?(?:bitcoin|btc|ethereum|eth|solana|sol|bnb|altcoin)',
            r'\b(expands|expanded|increases|increased|boosts|boosted)\s+(?:its\s+)?(?:treasury|holdings|reserves|portfolio)',
            r'\b(launches|launched|reveals|revealed|unveils|unveiled)\s+(?:new\s+)?(?:treasury|investment|acquisition)',
            r'\b(company|corp|inc|ltd|llc|foundation|protocol)\s+(?:announces|announced|adds|added|acquires|acquired)',
            r'\b(strategy|microstrategy|tesla|square|coinbase|binance|tether|matador|capital\s+b|sharplink|vivopower|bnc|trump\s+family)\s+(?:announces|announced|adds|added|acquires|acquired)',
            r'\b(announces|announced)\s+(?:strategic|new|major|significant)\s+(?:acquisition|investment|purchase|addition)',
            r'\b(announces|announced)\s+(?:plans\s+to\s+)?(?:expand|increase|boost)\s+(?:its\s+)?(?:treasury|holdings|reserves)',
            r'\b(announces|announced)\s+(?:a\s+)?(?:new\s+)?(?:treasury|investment|acquisition)\s+(?:strategy|initiative|program)'
        ]
        
        # Check if it contains specific company action language
        import re
        for pattern in company_action_patterns:
            if re.search(pattern, text):
                return True
                
        return False
    

    
    def normalize_title(self, title: str) -> str:
        """Normalize title for duplicate detection"""
        # Remove common prefixes and suffixes
        normalized = title.lower()
        
        # Remove common prefixes
        prefixes_to_remove = [
            'bitcoin news today:',
            'crypto news:',
            'breaking:',
            'latest:',
            'update:',
            'news:',
            'trending:'
        ]
        
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        # Remove source suffixes (e.g., " - Cryptopolitan")
        if ' - ' in normalized:
            normalized = normalized.split(' - ')[0].strip()
        
        # Extract key information (company, amount, action)
        import re
        
        # Extract company name and key numbers - expanded list
        company_pattern = r'\b(strategy|matador|capital\s+b|bitmine|tether|microstrategy|tesla|square|coinbase|binance|sharplink|vivopower|bnc|trump\s+family)\b'
        
        company_match = re.search(company_pattern, normalized)
        if not company_match:
            return normalized
        
        company = company_match.group(1)
        
        # Look for patterns like "buys 155 BTC" or "Adds 155 BTC" first
        acquisition_pattern = r'\b(buys?|adds?|acquires?|purchases?)\s+(\d+)\s*(btc|bitcoin|eth|ethereum|bnb|sol|ada|dot|link|avax|matic)\b'
        acquisition_match = re.search(acquisition_pattern, normalized)
        
        if acquisition_match:
            number = acquisition_match.group(2)
            crypto = acquisition_match.group(3)
            return f"{company} {number} {crypto}"
        
        # Fallback: look for the first number that appears with crypto in the title
        number_pattern = r'\b(\d+)\s*(btc|bitcoin|eth|ethereum|bnb|sol|ada|dot|link|avax|matic)\b'
        number_matches = list(re.finditer(number_pattern, normalized))
        
        if number_matches:
            # Take the first match (usually the acquisition amount)
            number = number_matches[0].group(1)
            crypto = number_matches[0].group(2)
            return f"{company} {number} {crypto}"
        
        # For announcements without specific numbers, use company + key action
        action_pattern = r'\b(announces|announced|adds|added|acquires|acquired|buys|bought|purchases|purchased)\b'
        action_match = re.search(action_pattern, normalized)
        if action_match:
            action = action_match.group(1)
            return f"{company} {action}"
        
        # Special handling for MicroStrategy to avoid duplicates
        if company == "strategy" or company == "microstrategy":
            # Look for specific amounts to differentiate
            amount_pattern = r'\b(\d+)\s*(btc|bitcoin|eth|ethereum)\b'
            amount_match = re.search(amount_pattern, normalized)
            if amount_match:
                amount = amount_match.group(1)
                crypto = amount_match.group(2)
                return f"microstrategy {amount} {crypto}"
            
            # Look for specific announcement patterns
            announcement_patterns = [
                r'\b(announces|announced)\s+(?:that\s+)?(?:it\s+)?(?:has\s+)?(?:will\s+)?(?:plans\s+to\s+)?(?:to\s+)?(?:add|acquire|buy|purchase|expand|increase)',
                r'\b(adds|added|acquires|acquired|buys|bought|purchases|purchased)\s+(?:an?\s+)?(?:additional\s+)?(?:more\s+)?(?:bitcoin|btc|ethereum|eth)',
                r'\b(expands|expanded|increases|increased|boosts|boosted)\s+(?:its\s+)?(?:treasury|holdings|reserves|portfolio)'
            ]
            
            for pattern in announcement_patterns:
                if re.search(pattern, normalized):
                    # Extract the action and any numbers
                    action_match = re.search(r'\b(announces?|announced|adds?|added|acquires?|acquired|buys?|bought|purchases?|purchased|expands?|expanded|increases?|increased|boosts?|boosted)\b', normalized)
                    if action_match:
                        action = action_match.group(1)
                        return f"microstrategy {action}"
            
            return "microstrategy announcement"
        
        return normalized
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse various date formats from RSS feeds"""
        try:
            # Try parsing RFC 822 format (most common in RSS)
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            try:
                # Try parsing without timezone
                return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
            except ValueError:
                try:
                    # Try ISO format
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Could not parse date: {date_str}")
                    return datetime.now()
    
    def fetch_news_from_rss(self, query: str) -> List[Dict[str, Any]]:
        """Fetch news from Google News RSS feed for a specific query"""
        try:
            rss_url = self.get_google_news_rss_url(query)
            logger.info(f"Fetching news from: {rss_url}")
            
            response = requests.get(rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML using xmltodict
            feed_data = xmltodict.parse(response.content)
            articles = []
            
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Extract items from RSS feed
            if 'rss' in feed_data and 'channel' in feed_data['rss']:
                channel = feed_data['rss']['channel']
                if 'item' in channel:
                    items = channel['item'] if isinstance(channel['item'], list) else [channel['item']]
                    
                    for item in items:
                        try:
                            # Parse the publication date
                            pub_date = self.parse_date(item.get('pubDate', ''))
                            
                            # Only include articles from the last 24 hours
                            if pub_date < cutoff_time:
                                continue
                            
                            # Check if it's a treasury expansion or new announcement
                            if self.is_treasury_expansion(item.get('title', ''), item.get('description', '')):
                                # Extract the actual article URL
                                actual_url = self.extract_actual_url(
                                    item.get('description', ''), 
                                    item.get('link', '')
                                )
                                
                                article = {
                                    'title': item.get('title', ''),
                                    'description': item.get('description', ''),
                                    'link': actual_url,
                                    'published': pub_date.isoformat(),
                                    'source': item.get('source', {}).get('title', 'Unknown') if isinstance(item.get('source'), dict) else 'Unknown',
                                    'query': query
                                }
                                articles.append(article)
                                logger.info(f"Found treasury expansion article: {item.get('title', '')}")
                                
                        except Exception as e:
                            logger.error(f"Error processing entry: {e}")
                            continue
                    
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed for query '{query}': {e}")
            return []
    
    def scrape_all_crypto_treasury_news(self) -> List[Dict[str, Any]]:
        """Scrape crypto treasury expansion news from multiple relevant queries"""
        queries = [
            "crypto treasury expansion",
            "bitcoin treasury acquisition",
            "ethereum treasury purchase",
            "solana treasury investment",
            "cardano treasury announcement",
            "polkadot treasury acquisition",
            "cryptocurrency treasury announcement",
            "crypto company adds bitcoin",
            "crypto company adds ethereum",
            "crypto company adds solana",
            "blockchain treasury investment",
            "defi treasury launch",
            "crypto balance sheet expansion",
            "digital asset treasury acquisition",
            "crypto investment announcement",
            "bitcoin treasury reserves increase",
            "ethereum holdings expansion",
            "solana holdings expansion",
            "altcoin treasury acquisition",
            "crypto company buys bitcoin",
            "crypto company buys ethereum",
            "crypto company buys altcoins",
            "treasury bitcoin acquisition",
            "treasury ethereum acquisition",
            "treasury altcoin acquisition",
            "crypto reserves announcement",
            "defi protocol treasury expansion",
            "nft treasury investment",
            "web3 treasury acquisition",
            "token treasury purchase"
        ]
        
        all_articles = []
        
        for query in queries:
            logger.info(f"Scraping news for query: {query}")
            articles = self.fetch_news_from_rss(query)
            all_articles.extend(articles)
            
            # Be respectful to the server
            time.sleep(2)
        
        # Remove duplicates based on link and similar titles
        seen_links = set()
        seen_titles = set()
        unique_articles = []
        
        for article in all_articles:
            # Check for duplicate links
            if article['link'] in seen_links:
                logger.info(f"Duplicate link found: {article['title']}")
                continue
                
            # Check for similar titles (normalize and compare)
            normalized_title = self.normalize_title(article['title'])
            if normalized_title in seen_titles:
                logger.info(f"Duplicate title found: {article['title']} -> {normalized_title}")
                continue
                
            seen_links.add(article['link'])
            seen_titles.add(normalized_title)
            unique_articles.append(article)
        
        # Sort by publication date (newest first)
        unique_articles.sort(key=lambda x: x['published'], reverse=True)
        
        self.news_data = unique_articles
        logger.info(f"Found {len(unique_articles)} unique crypto treasury expansion articles")
        
        return unique_articles
    
    def extract_actual_url(self, description: str, rss_link: str) -> str:
        """Extract the actual article URL from the description or follow redirect"""
        try:
            import re
            import urllib.parse
            
            # First, try to extract URL from the description
            # Google News RSS descriptions often contain the actual URL in an <a> tag
            href_pattern = r'href="([^"]+)"'
            href_match = re.search(href_pattern, description)
            if href_match:
                actual_url = href_match.group(1)
                # Remove Google News redirect parameters
                if 'news.google.com' in actual_url:
                    # Extract the actual URL from Google News redirect
                    url_match = re.search(r'url=([^&]+)', actual_url)
                    if url_match:
                        decoded_url = urllib.parse.unquote(url_match.group(1))
                        return decoded_url
                return actual_url
            
            # If no href found in description, try to extract from the RSS link itself
            if 'news.google.com' in rss_link:
                # Look for url parameter in the RSS link
                url_match = re.search(r'url=([^&]+)', rss_link)
                if url_match:
                    decoded_url = urllib.parse.unquote(url_match.group(1))
                    return decoded_url
            
            # If still no URL found, try to follow the RSS link redirect
            try:
                response = requests.head(rss_link, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    final_url = response.url
                    # If the final URL is still a Google News URL, try to extract the actual URL
                    if 'news.google.com' in final_url:
                        url_match = re.search(r'url=([^&]+)', final_url)
                        if url_match:
                            decoded_url = urllib.parse.unquote(url_match.group(1))
                            return decoded_url
                    return final_url
            except Exception as e:
                logger.warning(f"Error following redirect: {e}")
            
            # Fallback to the original RSS link
            return rss_link
            
        except Exception as e:
            logger.warning(f"Error extracting actual URL: {e}")
            return rss_link
    
    def save_to_json(self, filename: str = "crypto_treasury_news.json"):
        """Save scraped news to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'last_updated': datetime.now().isoformat(),
                    'articles': self.news_data
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"News data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def get_latest_news(self) -> List[Dict[str, Any]]:
        """Get the latest scraped news data"""
        return self.news_data

def main():
    """Main function to run the scraper"""
    scraper = CryptoNewsScraper()
    articles = scraper.scrape_all_crypto_treasury_news()
    scraper.save_to_json()
    
    print(f"\nFound {len(articles)} crypto treasury expansion articles from the last 24 hours:")
    for i, article in enumerate(articles[:5], 1):  # Show first 5 articles
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Published: {article['published']}")
        print(f"   Link: {article['link']}")

if __name__ == "__main__":
    main() 
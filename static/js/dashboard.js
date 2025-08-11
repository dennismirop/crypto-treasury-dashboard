// Crypto Treasury News Dashboard JavaScript

class CryptoNewsDashboard {
    constructor() {
        this.newsData = [];
        this.statsData = {};
        this.isRefreshing = false;
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshNews());
        }

        // Filter buttons
        const filterButtons = document.querySelectorAll('input[name="filterType"]');
        filterButtons.forEach(button => {
            button.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.renderNewsArticles();
            });
        });

        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.loadNewsData();
        }, 300000); // 5 minutes
    }

    async loadInitialData() {
        await Promise.all([
            this.loadNewsData(),
            this.loadStatsData()
        ]);
    }

    async loadNewsData() {
        try {
            const response = await fetch('/api/news');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.newsData = data.articles || [];
            
            this.updateLastUpdated(data.last_updated);
            this.renderNewsArticles();
            this.hideLoadingSpinner();
            
        } catch (error) {
            console.error('Error loading news data:', error);
            this.showError('Failed to load news data. Please try again.');
        }
    }

    async loadStatsData() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.statsData = data;
            
            this.updateStatistics();
            this.renderSidebarData();
            
        } catch (error) {
            console.error('Error loading stats data:', error);
        }
    }

    async refreshNews() {
        if (this.isRefreshing) return;
        
        this.isRefreshing = true;
        this.showRefreshingState();
        
        try {
            const response = await fetch('/api/refresh');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.newsData = data.articles || [];
            
            this.updateLastUpdated(data.last_updated);
            this.renderNewsArticles();
            
            // Show success message
            this.showSuccess('News refreshed successfully!');
            
        } catch (error) {
            console.error('Error refreshing news:', error);
            this.showError('Failed to refresh news. Please try again.');
        } finally {
            this.isRefreshing = false;
            this.hideRefreshingState();
        }
    }

    updateLastUpdated(timestamp) {
        const lastUpdatedElement = document.getElementById('last-updated');
        if (lastUpdatedElement && timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diffInMinutes = Math.floor((now - date) / (1000 * 60));
            
            let timeString;
            if (diffInMinutes < 1) {
                timeString = 'Just now';
            } else if (diffInMinutes < 60) {
                timeString = `${diffInMinutes}m ago`;
            } else if (diffInMinutes < 1440) {
                const hours = Math.floor(diffInMinutes / 60);
                timeString = `${hours}h ago`;
            } else {
                const days = Math.floor(diffInMinutes / 1440);
                timeString = `${days}d ago`;
            }
            
            lastUpdatedElement.textContent = timeString;
        }
    }

    updateStatistics() {
        // Update total articles
        const totalArticlesElement = document.getElementById('total-articles');
        if (totalArticlesElement) {
            totalArticlesElement.textContent = this.statsData.total_articles || 0;
        }

        // Update total sources
        const totalSourcesElement = document.getElementById('total-sources');
        if (totalSourcesElement) {
            const sourceCount = Object.keys(this.statsData.top_sources || {}).length;
            totalSourcesElement.textContent = sourceCount;
        }

        // Update total queries
        const totalQueriesElement = document.getElementById('total-queries');
        if (totalQueriesElement) {
            const queryCount = Object.keys(this.statsData.top_queries || {}).length;
            totalQueriesElement.textContent = queryCount;
        }
    }

    renderNewsArticles() {
        const container = document.getElementById('news-container');
        const noNewsElement = document.getElementById('no-news');
        const tableBody = document.getElementById('news-table-body');
        const filteredCountElement = document.getElementById('filtered-count');
        const totalCountElement = document.getElementById('total-count');
        
        if (!container || !tableBody) return;
        
        if (this.newsData.length === 0) {
            container.classList.add('d-none');
            if (noNewsElement) {
                noNewsElement.classList.remove('d-none');
            }
            return;
        }
        
        if (noNewsElement) {
            noNewsElement.classList.add('d-none');
        }
        
        container.classList.remove('d-none');
        tableBody.innerHTML = '';
        
        // Remove duplicates based on link
        const uniqueArticles = this.removeDuplicateArticles(this.newsData);
        
        // Apply filter
        const filteredArticles = this.filterArticles(uniqueArticles);
        
        // Update count display
        if (totalCountElement) {
            totalCountElement.textContent = uniqueArticles.length;
        }
        if (filteredCountElement) {
            filteredCountElement.textContent = filteredArticles.length;
        }
        
        filteredArticles.forEach(article => {
            const rowElement = this.createNewsTableRow(article);
            tableBody.appendChild(rowElement);
        });
        
        // Show no results message if filter returns no articles
        if (filteredArticles.length === 0 && uniqueArticles.length > 0) {
            const noResultsRow = document.createElement('tr');
            noResultsRow.innerHTML = `
                <td colspan="4" class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-3"></i>
                    <h6>No articles match the current filter</h6>
                    <p class="small">Try selecting a different filter option</p>
                </td>
            `;
            tableBody.appendChild(noResultsRow);
        }
    }

    removeDuplicateArticles(articles) {
        const seenLinks = new Set();
        const seenTitles = new Set();
        
        return articles.filter(article => {
            // Check for duplicate links
            if (seenLinks.has(article.link)) {
                return false;
            }
            
            // Check for similar titles (normalize and compare)
            const normalizedTitle = this.normalizeTitle(article.title);
            if (seenTitles.has(normalizedTitle)) {
                return false;
            }
            
            seenLinks.add(article.link);
            seenTitles.add(normalizedTitle);
            return true;
        });
    }

    filterArticles(articles) {
        if (this.currentFilter === 'all') {
            return articles;
        }
        
        return articles.filter(article => {
            const articleType = this.getArticleType(article);
            
            if (this.currentFilter === 'expansions') {
                // Show expansions and new announcements (exclude general treasury activity)
                return articleType === 'Expansion' || 
                       articleType === 'New Announcement' || 
                       articleType === 'Expansion & Announcement';
            } else if (this.currentFilter === 'announcements') {
                // Show only new announcements
                return articleType === 'New Announcement' || 
                       articleType === 'Expansion & Announcement';
            }
            
            return true;
        });
    }

    normalizeTitle(title) {
        // Remove common prefixes and suffixes
        let normalized = title.toLowerCase();
        
        // Remove common prefixes
        const prefixesToRemove = [
            'bitcoin news today:',
            'crypto news:',
            'breaking:',
            'latest:',
            'update:'
        ];
        
        for (const prefix of prefixesToRemove) {
            if (normalized.startsWith(prefix)) {
                normalized = normalized.substring(prefix.length).trim();
            }
        }
        
        // Remove source suffixes (e.g., " - Cryptopolitan")
        if (normalized.includes(' - ')) {
            normalized = normalized.split(' - ')[0].trim();
        }
        
        // Extract key information (company, amount, action)
        // Look for patterns like "Strategy buys 155 BTC" or "Strategy Adds 155 BTC"
        const companyPattern = /\b(strategy|matador|capital\s+b|bitmine|tether|microstrategy|tesla|square|coinbase|binance)\b/;
        
        // Look for patterns like "buys 155 BTC" or "Adds 155 BTC" - focus on the acquisition amount
        const acquisitionPattern = /\b(buys?|adds?|acquires?|purchases?)\s+(\d+)\s*(btc|bitcoin|eth|ethereum)\b/;
        
        const companyMatch = normalized.match(companyPattern);
        const acquisitionMatch = normalized.match(acquisitionPattern);
        
        if (companyMatch && acquisitionMatch) {
            const company = companyMatch[1];
            const number = acquisitionMatch[2];
            const crypto = acquisitionMatch[3];
            return `${company} ${number} ${crypto}`;
        }
        
        // Special handling for MicroStrategy to avoid duplicates
        if (companyMatch && (companyMatch[1] === 'strategy' || companyMatch[1] === 'microstrategy')) {
            // Look for specific amounts to differentiate
            const amountPattern = /\b(\d+)\s*(btc|bitcoin|eth|ethereum)\b/;
            const amountMatch = normalized.match(amountPattern);
            if (amountMatch) {
                const amount = amountMatch[1];
                const crypto = amountMatch[2];
                return `microstrategy ${amount} ${crypto}`;
            }
            
            // Look for specific announcement patterns
            const announcementPatterns = [
                /\b(announces?|announced)\s+(?:that\s+)?(?:it\s+)?(?:has\s+)?(?:will\s+)?(?:plans\s+to\s+)?(?:to\s+)?(?:add|acquire|buy|purchase|expand|increase)/,
                /\b(adds?|added|acquires?|acquired|buys?|bought|purchases?|purchased)\s+(?:an?\s+)?(?:additional\s+)?(?:more\s+)?(?:bitcoin|btc|ethereum|eth)/,
                /\b(expands?|expanded|increases?|increased|boosts?|boosted)\s+(?:its\s+)?(?:treasury|holdings|reserves|portfolio)/
            ];
            
            for (const pattern of announcementPatterns) {
                if (pattern.test(normalized)) {
                    // Extract the action
                    const actionMatch = normalized.match(/\b(announces?|announced|adds?|added|acquires?|acquired|buys?|bought|purchases?|purchased|expands?|expanded|increases?|increased|boosts?|boosted)\b/);
                    if (actionMatch) {
                        const action = actionMatch[1];
                        return `microstrategy ${action}`;
                    }
                }
            }
            
            return 'microstrategy announcement';
        }
        
        // Fallback: look for any number followed by crypto
        const numberPattern = /\b(\d+)\s*(btc|bitcoin|eth|ethereum)\b/;
        const numberMatch = normalized.match(numberPattern);
        
        if (companyMatch && numberMatch) {
            const company = companyMatch[1];
            const number = numberMatch[1];
            const crypto = numberMatch[2];
            return `${company} ${number} ${crypto}`;
        }
        
        // Remove extra whitespace and normalize
        normalized = normalized.replace(/\s+/g, ' ').trim();
        
        return normalized;
    }

    getArticleType(article) {
        const text = `${article.title} ${article.description || ''}`.toLowerCase();
        
        // Primary expansion keywords (strong indicators)
        const primaryExpansionKeywords = [
            'buys', 'bought', 'purchases', 'purchased', 'purchase',
            'acquires', 'acquired', 'acquisition',
            'adds', 'added', 'addition'
        ];
        
        // Secondary expansion keywords (weaker indicators)
        const secondaryExpansionKeywords = [
            'expands', 'expanded', 'expansion', 'increases', 'increased', 'increase',
            'boosts', 'boosted', 'boost', 'grows', 'grew', 'growth'
        ];
        
        // Primary announcement keywords (strong indicators)
        const primaryAnnouncementKeywords = [
            'announces', 'announced', 'announcement',
            'launches', 'launched', 'launch',
            'reveals', 'revealed', 'reveal',
            'unveils', 'unveiled', 'unveil'
        ];
        
        // Secondary announcement keywords (weaker indicators)
        const secondaryAnnouncementKeywords = [
            'new', 'fresh', 'latest', 'recent', 'updates', 'updated',
            'strategic', 'investment', 'portfolio'
        ];
        
        // Check for primary expansion keywords
        const hasPrimaryExpansion = primaryExpansionKeywords.some(keyword => text.includes(keyword));
        const hasSecondaryExpansion = secondaryExpansionKeywords.some(keyword => text.includes(keyword));
        
        // Check for primary announcement keywords
        const hasPrimaryAnnouncement = primaryAnnouncementKeywords.some(keyword => text.includes(keyword));
        const hasSecondaryAnnouncement = secondaryAnnouncementKeywords.some(keyword => text.includes(keyword));
        
        // Determine type based on priority
        if (hasPrimaryExpansion && hasPrimaryAnnouncement) {
            return 'Expansion & Announcement';
        } else if (hasPrimaryExpansion) {
            return 'Expansion';
        } else if (hasPrimaryAnnouncement) {
            return 'New Announcement';
        } else if (hasSecondaryExpansion && hasSecondaryAnnouncement) {
            return 'Treasury Activity';
        } else if (hasSecondaryExpansion) {
            return 'Expansion';
        } else if (hasSecondaryAnnouncement) {
            return 'New Announcement';
        } else {
            return 'Treasury Activity';
        }
    }



    createNewsTableRow(article) {
        const row = document.createElement('tr');
        row.className = 'table-row-hover';
        
        const publishedDate = new Date(article.published);
        const formattedDate = publishedDate.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const articleType = this.getArticleType(article);
        
        // Determine badge color based on type
        let badgeClass = 'badge bg-secondary';
        if (articleType === 'Expansion') {
            badgeClass = 'badge bg-success';
        } else if (articleType === 'New Announcement') {
            badgeClass = 'badge bg-primary';
        } else if (articleType === 'Expansion & Announcement') {
            badgeClass = 'badge bg-warning text-dark';
        }
        
        row.innerHTML = `
            <td>
                <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="text-decoration-none fw-medium">
                    ${this.escapeHtml(article.title)}
                </a>
            </td>
            <td>
                <span class="${badgeClass}">${articleType}</span>
            </td>
            <td class="text-muted">${formattedDate}</td>
            <td class="text-muted small">${this.escapeHtml(article.source)}</td>
        `;
        
        return row;
    }

    renderSidebarData() {
        this.renderTopSources();
        this.renderSearchQueries();
    }

    renderTopSources() {
        const container = document.getElementById('sources-container');
        if (!container) return;
        
        const sources = this.statsData.top_sources || {};
        const sourceEntries = Object.entries(sources).sort((a, b) => b[1] - a[1]);
        
        if (sourceEntries.length === 0) {
            container.innerHTML = '<p class="text-muted small">No sources found</p>';
            return;
        }
        
        const list = document.createElement('ul');
        list.className = 'sidebar-list';
        
        sourceEntries.forEach(([source, count]) => {
            const item = document.createElement('li');
            item.className = 'sidebar-item';
            item.innerHTML = `
                <span class="sidebar-label text-truncate">${this.escapeHtml(source)}</span>
                <span class="sidebar-count">${count}</span>
            `;
            list.appendChild(item);
        });
        
        container.innerHTML = '';
        container.appendChild(list);
    }

    renderSearchQueries() {
        const container = document.getElementById('queries-container');
        if (!container) return;
        
        const queries = this.statsData.top_queries || {};
        const queryEntries = Object.entries(queries).sort((a, b) => b[1] - a[1]);
        
        if (queryEntries.length === 0) {
            container.innerHTML = '<p class="text-muted small">No queries found</p>';
            return;
        }
        
        const list = document.createElement('ul');
        list.className = 'sidebar-list';
        
        queryEntries.forEach(([query, count]) => {
            const item = document.createElement('li');
            item.className = 'sidebar-item';
            item.innerHTML = `
                <span class="sidebar-label text-truncate">${this.escapeHtml(query)}</span>
                <span class="sidebar-count">${count}</span>
            `;
            list.appendChild(item);
        });
        
        container.innerHTML = '';
        container.appendChild(list);
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        
        if (diffInMinutes < 1) {
            return 'Just now';
        } else if (diffInMinutes < 60) {
            return `${diffInMinutes}m ago`;
        } else if (diffInMinutes < 1440) {
            const hours = Math.floor(diffInMinutes / 60);
            return `${hours}h ago`;
        } else {
            const days = Math.floor(diffInMinutes / 1440);
            return `${days}d ago`;
        }
    }

    showRefreshingState() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-2 refreshing"></i>Refreshing...';
        }
    }

    hideRefreshingState() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Refresh News';
        }
    }

    hideLoadingSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.classList.add('d-none');
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    startAutoRefresh() {
        // Auto-refresh every 30 minutes
        setInterval(() => {
            this.loadNewsData();
            this.loadStatsData();
        }, 1800000); // 30 minutes
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CryptoNewsDashboard();
}); 
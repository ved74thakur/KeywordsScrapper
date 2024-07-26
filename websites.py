from pytrends.request import TrendReq
import re

def get_trending_news_sites():
    pytrends = TrendReq(hl='en-IN', tz=330)
    
    # Get trending searches for India
    trending_searches_df = pytrends.trending_searches(pn='india')
    
    # Assuming news sites typically have these patterns
    news_site_patterns = [
        r'https?://[^\s]+\.com',
        r'https?://[^\s]+\.in',
        r'https?://[^\s]+\.org',
        r'https?://[^\s]+\.net'
    ]
    
    news_sites = set()
    for query in trending_searches_df[0]:
        # Since `suggestions` might not return URLs, we just print trending searches
        # and search for patterns manually in a real scenario
        print(f"Trending Query: {query}")
    
    return list(news_sites)[:5]  # Return top 5 news sites (if any)

urls = get_trending_news_sites()
for url in urls:
    print(url)

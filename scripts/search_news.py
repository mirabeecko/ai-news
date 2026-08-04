#!/usr/bin/env python3
"""Search for latest AI news from Aug 1-3, 2026 using HTTP requests."""
import json, re, ssl, sys, hashlib, datetime
from urllib.request import Request, urlopen
from urllib.parse import quote

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
ctx = ssl.create_default_context()

def fetch_url(url, timeout=15):
    req = Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml'})
    return urlopen(req, context=ctx, timeout=timeout).read().decode('utf-8', errors='replace')

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def extract_headlines(html):
    """Extract headlines from various HTML patterns."""
    results = []
    # Try meta tags
    for m in re.finditer(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html):
        results.append(m.group(1))
    # Try h2/h3
    for m in re.finditer(r'<(h2|h3)[^>]*>(.*?)</\1>', html, re.DOTALL):
        text = clean_html(m.group(2))
        if len(text) > 20 and len(text) < 200:
            results.append(text)
    # Try article title patterns  
    for m in re.finditer(r'<a[^>]*>(.*?)</a>', html, re.DOTALL):
        text = clean_html(m.group(1))
        if len(text) > 30 and len(text) < 250:
            results.append(text)
    return results

def search_newsapi(query, from_date='2026-08-01'):
    """Use NewsAPI to search (without API key, try their public endpoint)."""
    # Without API key, try the newsapi.org /v2/everything
    # But that requires a key. Let's try alternative approaches.

# Alternative: Search via Bing
def search_bing(query):
    results = []
    try:
        url = f'https://www.bing.com/search?q={quote(query)}&filters=ex1:"ez3"&qft=interval%3d"7"'
        html = fetch_url(url, timeout=10)
        # Extract search results
        for m in re.finditer(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html):
            url = m.group(1)
            title = clean_html(m.group(2))
            if title:
                results.append({'title': title, 'url': url})
        # Also try alternative Bing patterns
        for m in re.finditer(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html):
            t = clean_html(m.group(2))
            if len(t) > 30:
                results.append({'title': t, 'url': m.group(1)})
    except Exception as e:
        print(f"  Bing error: {e}", file=sys.stderr)
    return results

# Direct site scraping
def check_site(url, label):
    print(f"\n=== {label} ===", file=sys.stderr)
    try:
        html = fetch_url(url, timeout=15)
        headlines = extract_headlines(html)
        for h in headlines[:15]:
            # Filter for AI-related
            if any(kw in h.lower() for kw in ['ai', 'model', 'gpt', 'claude', 'gemini', 'llm', 'openai', 'anthropic', 'robot', 'agent']):
                print(f"  {h}")
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)

if __name__ == '__main__':
    # Sites to check
    sites = [
        ('https://techcrunch.com/category/artificial-intelligence/', 'TechCrunch AI'),
        ('https://www.theverge.com/ai-artificial-intelligence', 'The Verge AI'),
        ('https://arstechnica.com/ai/', 'Ars Technica AI'),
        ('https://venturebeat.com/category/ai/', 'VentureBeat AI'),
    ]
    
    for url, label in sites:
        check_site(url, label)
    
    # Try Bing search for recent AI news
    print("\n=== Bing: AI news August 2026 ===", file=sys.stderr)
    results = search_bing('AI news August 2026')
    for r in results[:10]:
        print(f"  {r['title']}")
        print(f"    {r['url']}")

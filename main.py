import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
from pytrends.request import TrendReq
import re
import os

load_dotenv()

def get_trending_news_sites():
    pytrends = TrendReq(hl='en-IN', tz=330)
    trending_searches_df = pytrends.trending_searches(pn='india')
    
    news_sites = set()
    news_site_pattern = re.compile(r'https?://[^\s]+')
    
    for query in trending_searches_df[0]:
        search_results = pytrends.suggestions(query)
        for result in search_results:
            title = result.get('title', '')
            news_sites.update(re.findall(news_site_pattern, title))
    
    return list(news_sites)

def scrape_keywords(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    keywords_meta = soup.find('meta', {'name': 'keywords'})
    if keywords_meta:
        keywords = keywords_meta.get('content', '').split(',')
        return [keyword.strip() for keyword in keywords]
    return []

def save_keywords_to_json(all_keywords, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(all_keywords, json_file)

def upload_to_firebase_storage(file_path, storage_path):
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    blob.upload_from_filename(file_path)
    blob.make_public()
    public_url = blob.public_url
    print(f'Uploaded {file_path} to Firebase Storage as {storage_path}')
    print(f'Public URL: {public_url}')
    return public_url

def store_keywords_in_firestore(all_keywords, public_url):
    aggregated_keywords = {}
    for url, keywords in all_keywords.items():
        aggregated_keywords[url] = keywords
        
    db.collection('keywords').document('all_keywords').set({
        'data': aggregated_keywords,
        'public_url': public_url
    })
    print('Stored keywords in Firestore.')

def main():
    urls = [
        'https://timesofindia.indiatimes.com/', 
        'https://economictimes.indiatimes.com/defaultinterstitial.cms',
        'https://www.indiatimes.com/',
        'https://www.livemint.com/',
        'https://www.ndtv.com/'
    ]
    # urls = get_trending_news_sites()
    all_keywords = {}

    for url in urls:
        keywords = scrape_keywords(url)
        all_keywords[url] = keywords

    print(all_keywords)

    json_file_path = 'keywords.json'
    save_keywords_to_json(all_keywords, json_file_path)

    public_url = upload_to_firebase_storage(json_file_path, 'keywords/keywords.json')

    store_keywords_in_firestore(all_keywords, public_url)

if __name__ == "__main__":
    cred_path = os.getenv('FIREBASE_CREDENTIALS')
    storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': storage_bucket
    })
    db = firestore.client()
    main()

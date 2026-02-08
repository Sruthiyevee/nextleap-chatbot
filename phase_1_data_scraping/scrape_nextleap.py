import os
import requests
from bs4 import BeautifulSoup
import json
import time

# Directory to save scraped data
DATA_DIR = "scraped_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Base URL
BASE_URL = "https://nextleap.app"

# Pages to scrape
PAGES_TO_SCRAPE = [
    {"url": BASE_URL, "name": "homepage"},
    {"url": f"{BASE_URL}/reviews", "name": "reviews"},
    {"url": f"{BASE_URL}/for-companies", "name": "hire_from_us"},
    {"url": f"{BASE_URL}/blog/", "name": "blog_main"},
    # We can add more specific fellowship pages if we find them during crawling
    {"url": f"{BASE_URL}/fellowship/product-manager", "name": "pm_fellowship"}, # Hypothetical URL, trying common pattern
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_text(text):
    """
    Simple text cleaning: remove extra whitespace.
    """
    if not text:
        return ""
    return " ".join(text.split())

def scrape_page(url, name):
    print(f"Scraping {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract text
        text = soup.get_text()
        
        # Clean text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Save raw text
        with open(os.path.join(DATA_DIR, f"{name}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
            
        # Find links for further crawling (simple 1-level depth idea)
        links = []
        for a in soup.find_all('a', href=True):
            links.append({
                "text": clean_text(a.get_text()),
                "href": a['href']
            })
            
        # Save metadata and links
        metadata = {
            "url": url,
            "title": soup.title.string if soup.title else "No Title",
            "links_found": links
        }
        
        with open(os.path.join(DATA_DIR, f"{name}_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Successfully scraped {name}")
        return True
        
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return False

def main():
    print("Starting scraping process...")
    for page in PAGES_TO_SCRAPE:
        scrape_page(page["url"], page["name"])
        time.sleep(1) # Be polite
    print("Scraping completed.")

if __name__ == "__main__":
    main()

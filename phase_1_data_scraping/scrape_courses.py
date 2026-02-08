import os
import requests
from bs4 import BeautifulSoup
import json
import time

DATA_DIR = "scraped_courses"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

COURSE_URLS = [
    "https://nextleap.app/course/product-management-course",
    "https://nextleap.app/course/ui-ux-design-course",
    "https://nextleap.app/course/data-analyst-course",
    "https://nextleap.app/course/business-analyst-course",
    "https://nextleap.app/course/generative-ai-course"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_course(url):
    course_slug = url.split("/")[-1]
    print(f"Scraping {course_slug}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract text clearly preserving some structure
        text = soup.get_text(separator='\n')
        
        # Clean text
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        # Save raw text
        with open(os.path.join(DATA_DIR, f"{course_slug}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"[{course_slug}] Saved.")
        
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

def main():
    for url in COURSE_URLS:
        scrape_course(url)
        time.sleep(1)

if __name__ == "__main__":
    main()

import os
import re
import time
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Configuration
AWS_WHITEPAPER_URL = ("https://aws.amazon.com/en/whitepapers/"
                      "?whitepapers-main.sort-by=item.additionalFields.sortDate"
                      "&whitepapers-main.sort-order=desc")
OUTPUT_DIR = "aws_whitepapers"
PAGE_LOAD_DELAY = 3

# Category definitions moved to a separate config file for better maintenance
from categories import CATEGORIES, CATEGORY_ORDER

def download_file(url, filepath):
    """Download a file from URL to the specified filepath."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Downloaded: {filepath}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def get_clean_filename(url):
    """Extract and clean filename from URL."""
    basename = os.path.basename(urlparse(url).path)
    match = re.search(r'(.*\.pdf)', basename, re.IGNORECASE)
    filename = match.group(1) if match else basename
    
    if filename == '.pdf' or len(filename) < 5:
        return None
        
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def is_valid_pdf_link(href):
    """Check if URL is a valid PDF link."""
    if not href or 'shareArticle' in href or 'sharer.php' in href:
        return False
    
    filename = href.rsplit('/', 1)[-1].strip()
    return not (filename.lower() == '.pdf' or len(filename) < 5)

def determine_category(url, title):
    """Determine category based on URL and title."""
    text_to_match = (url + title).lower()
    
    for category_name in CATEGORY_ORDER:
        if any(keyword in text_to_match for keyword in CATEGORIES[category_name]):
            return category_name
    
    return 'misc'

def scrape_pdf_urls():
    """Scrape PDF URLs from AWS Whitepapers page."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en'})
    driver = webdriver.Chrome(options=options)
    pdf_urls = set()
    
    try:
        driver.get(AWS_WHITEPAPER_URL)
        time.sleep(PAGE_LOAD_DELAY)

        while True:
            print("Processing page...")
            
            # Collect PDF links
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='.pdf']")
            pdf_urls.update(
                link.get_attribute("href") 
                for link in links 
                if is_valid_pdf_link(link.get_attribute("href"))
            )
            
            # Try to go to next page
            try:
                next_link = driver.find_element(By.CSS_SELECTOR, "a.m-icon-angle-right.m-active")
                if not next_link.is_displayed():
                    break
                next_link.click()
                time.sleep(PAGE_LOAD_DELAY)
            except NoSuchElementException:
                break

    finally:
        driver.quit()
        
    return pdf_urls

def main():
    """Main execution function."""
    # Get PDF URLs
    pdf_urls = scrape_pdf_urls()
    
    # Setup output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.chdir(OUTPUT_DIR)
    
    # Download PDFs
    for pdf_url in pdf_urls:
        filename = get_clean_filename(pdf_url)
        if not filename:
            continue
            
        category = determine_category(pdf_url, filename)
        os.makedirs(category, exist_ok=True)
        
        filepath = os.path.join(category, filename)
        download_file(pdf_url, filepath)
    
    # Print summary
    print("\nDownload Summary:")
    for category in os.listdir('.'):
        if os.path.isdir(category):
            count = len(os.listdir(category))
            print(f"{category}: {count} files")

if __name__ == "__main__":
    main()
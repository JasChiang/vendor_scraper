#!/usr/bin/env python3
"""
Vendor Scraper for PetsShow Taipei
This script scrapes vendor names and their official website URLs from the PetsShow Taipei website.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from urllib.parse import urljoin

# Base URL
BASE_URL = "https://www.chanchao.com.tw/petsshow/taipei/"
EXHIBITOR_URL = urljoin(BASE_URL, "visitorExhibitor.asp")

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

def get_soup(url, params=None):
    """Get BeautifulSoup object from URL"""
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.encoding = 'utf-8'  # Ensure correct encoding for Chinese characters
        
        if response.status_code != 200:
            print(f"Error fetching {url}: Status code {response.status_code}")
            return None
        
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_vendor_info(detail_url):
    """Extract vendor's name and official website from detail page"""
    soup = get_soup(detail_url)
    if not soup:
        return None, None
    
    # Extract vendor name from the page title or h1
    vendor_name = None
    h1_element = soup.find('h1')
    if h1_element:
        vendor_name = h1_element.text.strip()
    
    if not vendor_name:
        title_element = soup.find('title')
        if title_element:
            title_text = title_element.text.strip()
            # Extract vendor name from title (usually in format "Vendor Name - Exhibition Name")
            if '-' in title_text:
                vendor_name = title_text.split('-')[0].strip()
    
    # Extract website URL
    website = None
    
    # Method 1: Look for "公司網址：" text directly using regex
    company_website_pattern = re.compile(r'公司網址：\s*(https?://[^\s<>"\']+)')
    html_content = str(soup)
    match = company_website_pattern.search(html_content)
    if match:
        website = match.group(1)
        print(f"Found website using regex pattern: {website}")
    
    # Method 2: Look for elements containing "公司網址："
    if not website:
        for element in soup.find_all(['p', 'div', 'span', 'td', 'li']):
            if element.text and "公司網址：" in element.text:
                text = element.text.strip()
                # Extract the URL part after "公司網址："
                website_part = text.split("公司網址：")[-1].strip()
                
                # Try to extract a URL from the text
                url_match = re.search(r'(https?://[^\s<>"\']+)', website_part)
                if url_match:
                    website = url_match.group(1)
                    print(f"Found website in element text: {website}")
                    break
                else:
                    # If no http/https prefix, check if it starts with www or has domain extensions
                    domain_match = re.search(r'(www\.[^\s<>"\']+)', website_part)
                    if domain_match:
                        website = "http://" + domain_match.group(1)
                        print(f"Found website domain (added http://): {website}")
                        break
                    
                    # Check for common domain extensions
                    domain_ext_match = re.search(r'([^\s<>"\']+\.(com|org|net|tw|io|co)([^\s<>"\']*)?)', website_part)
                    if domain_ext_match:
                        website = "http://" + domain_ext_match.group(0)
                        print(f"Found website domain with extension (added http://): {website}")
                        break
    
    # Method 3: Look for a link element that might be the website
    if not website:
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if (href and 
                href.startswith(('http://', 'https://')) and 
                'chanchao.com.tw' not in href and
                not href.startswith(('mailto:', 'tel:'))):
                
                # Check if this link is near "公司網址："
                parent_text = link.parent.text if link.parent else ""
                if "公司網址" in parent_text:
                    website = href
                    print(f"Found website link near '公司網址': {website}")
                    break
    
    return vendor_name, website

def scrape_vendor_list(page_num=1):
    """Scrape the vendor list from a single page"""
    print(f"Scraping vendor list from page {page_num}...")
    params = {"page": page_num} if page_num > 1 else None
    soup = get_soup(EXHIBITOR_URL, params)
    
    if not soup:
        return [], False
    
    vendors = []
    
    # Find the vendor list (ul with class="product")
    product_ul = soup.find('ul', class_='product')
    
    if not product_ul:
        print(f"No vendor list found on page {page_num}")
        return [], False
    
    # Find all vendor items (li elements)
    vendor_items = product_ul.find_all('li')
    print(f"Found {len(vendor_items)} vendors on page {page_num}")
    
    for item in vendor_items:
        # Find the vendor link (a element)
        link = item.find('a', href=lambda href: href and 'visitorExhibitorDetail.asp' in href)
        
        if link:
            detail_url = urljoin(BASE_URL, link.get('href'))
            print(f"Processing detail URL: {detail_url}")
            
            # Get vendor name and website from detail page
            vendor_name, official_website = get_vendor_info(detail_url)
            
            if vendor_name and official_website:
                vendors.append({
                    'vendor_name': vendor_name,
                    'official_website': official_website
                })
                
                print(f"Scraped: {vendor_name} | Website: {official_website}")
            
            # Add a small delay to avoid overloading the server
            time.sleep(1)
    
    # Check if there's a next page
    has_next = False
    pagination = soup.find_all('a', href=lambda href: href and 'page=' in href)
    if pagination:
        max_page = 1
        for a in pagination:
            match = re.search(r'page=(\d+)', a.get('href'))
            if match:
                page_num_found = int(match.group(1))
                max_page = max(max_page, page_num_found)
        
        has_next = page_num < max_page
    
    return vendors, has_next

def main():
    """Main function to scrape all pages"""
    all_vendors = []
    page_num = 1
    has_next = True
    
    # Create output directory if it doesn't exist
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_csv = os.path.join(output_dir, 'vendors_data.csv')
    output_excel = os.path.join(output_dir, 'vendors_data.xlsx')
    
    try:
        while has_next:
            vendors, has_next = scrape_vendor_list(page_num)
            all_vendors.extend(vendors)
            
            # Save intermediate results after each page
            df = pd.DataFrame(all_vendors)
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            df.to_excel(output_excel, index=False)
            
            print(f"Saved {len(all_vendors)} vendors so far...")
            
            # Add a delay between pages
            if has_next:
                print(f"Moving to page {page_num + 1}...")
                page_num += 1
                time.sleep(2)
        
        print(f"Scraping completed. Total vendors scraped: {len(all_vendors)}")
        
    except KeyboardInterrupt:
        print("Scraping interrupted by user.")
        # Save what we have so far
        if all_vendors:
            df = pd.DataFrame(all_vendors)
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            df.to_excel(output_excel, index=False)
            print(f"Saved {len(all_vendors)} vendors before interruption.")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        # Save what we have so far
        if all_vendors:
            df = pd.DataFrame(all_vendors)
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            df.to_excel(output_excel, index=False)
            print(f"Saved {len(all_vendors)} vendors before error occurred.")

if __name__ == "__main__":
    main()

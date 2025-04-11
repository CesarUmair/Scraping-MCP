import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.browser = None
        
    async def initialize(self):
        """Initialize the browser."""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
        
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            
    async def scrape_url(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: The URL to scrape
            config: Configuration for the scraper including CSS selectors
                - title_selector: CSS selector for the title
                - content_selector: CSS selector for the main content
                - date_selector: CSS selector for the date
                - author_selector: CSS selector for the author
        
        Returns:
            A dictionary containing the scraped content
        """
        try:
            await self.initialize()
            page = await self.browser.new_page()
            
            # Set default headers to mimic a browser
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            # Navigate to the URL
            await page.goto(url, wait_until="networkidle")
            
            # Wait for content to load
            if "wait_for" in config:
                await page.wait_for_selector(config["wait_for"])
                
            # Get page content
            html_content = await page.content()
            
            # Close the page
            await page.close()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract relevant information
            title = self._extract_text(soup, config.get("title_selector"))
            content = self._extract_text(soup, config.get("content_selector"))
            date_str = self._extract_text(soup, config.get("date_selector"))
            author = self._extract_text(soup, config.get("author_selector"))
            
            # Try to parse date
            date = None
            if date_str:
                date = self._parse_date(date_str)
            
            return {
                "title": title,
                "raw_content": content,
                "clean_content": self._clean_text(content),
                "date": date,
                "url": url,
                "metadata": {
                    "author": author,
                    "scrape_date": datetime.now().isoformat(),
                }
            }
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise
    
    def _extract_text(self, soup: BeautifulSoup, selector: Optional[str]) -> Optional[str]:
        """Extract text from a BeautifulSoup object using a CSS selector."""
        if not selector:
            return None
            
        elements = soup.select(selector)
        if not elements:
            return None
            
        return elements[0].get_text(strip=True)
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean text by removing extra whitespace and normalizing."""
        if not text:
            return None
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse a date string into a standardized format."""
        try:
            # Try common date formats
            date_formats = [
                "%B %d, %Y",           # January 1, 2023
                "%d %B %Y",            # 1 January 2023
                "%Y-%m-%d",            # 2023-01-01
                "%m/%d/%Y",            # 01/01/2023
                "%d/%m/%Y",            # 01/01/2023
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt).date().isoformat()
                except ValueError:
                    continue
                    
            return None
        except Exception:
            return None 
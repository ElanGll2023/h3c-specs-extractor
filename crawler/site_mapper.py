"""
Site Mapper - Discovers all product pages on H3C website
"""
import re
import json
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from loguru import logger
import requests
from bs4 import BeautifulSoup


@dataclass
class ProductModel:
    """Represents a switch model."""
    model: str
    series: str
    name: str
    url: str
    category: str  # 'core', 'aggregation', 'access'
    doc_url: Optional[str] = None


@dataclass
class ProductSeries:
    """Represents a product series."""
    name: str
    url: str
    category: str
    models: List[ProductModel] = None

    def __post_init__(self):
        if self.models is None:
            self.models = []


class H3CSiteMapper:
    """Maps H3C website structure and discovers products."""

    BASE_URL = "https://www.h3c.com/en/"

    # Campus switch product page URLs
    CAMPUS_URLS = {
        'core': "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Core_Switch/",
        'aggregation': "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Aggregation/",
        'access': "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Access_Switch/",
    }

    def __init__(self, delay: float = 2.0, cache_dir: Optional[str] = None):
        self.delay = delay
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.discovered_models: List[ProductModel] = []
        self.discovered_series: List[ProductSeries] = []

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page with error handling and delay."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(self.delay)
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def discover_campus_switches(self) -> List[ProductModel]:
        """Discover all campus switch models."""
        all_models = []

        for category, url in self.CAMPUS_URLS.items():
            logger.info(f"Discovering {category} switches...")
            models = self._discover_category(url, category)
            all_models.extend(models)
            logger.info(f"Found {len(models)} {category} switches")

        self.discovered_models = all_models
        return all_models

    def _discover_category(self, url: str, category: str) -> List[ProductModel]:
        """Discover models in a category."""
        html = self.fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        models = []

        # Try to find product links
        # H3C product pages typically have product cards or lists
        product_links = self._extract_product_links(soup, url)

        for link in product_links:
            model = self._parse_product_page(link, category)
            if model:
                models.append(model)

        return models

    def _extract_product_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract product detail page links from a category page."""
        links = []

        # Look for product links - common patterns on H3C site
        # Pattern 1: Product cards with links
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Filter for product detail pages
            if '/Products/' in href or '/Product/' in href:
                full_url = urljoin(base_url, href)
                links.append(full_url)

        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        return unique_links

    def _parse_product_page(self, url: str, category: str) -> Optional[ProductModel]:
        """Parse a product detail page to extract model information."""
        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')

        # Extract model name from page title or content
        # Common patterns: "H3C S5590-EI Series ..."
        title = soup.find('title')
        if title:
            model_match = re.search(r'(S\d+[\w\-]+)', title.get_text())
            if model_match:
                model = model_match.group(1)
                series = self._extract_series(model)

                return ProductModel(
                    model=model,
                    series=series,
                    name=self._extract_product_name(soup),
                    url=url,
                    category=category,
                    doc_url=self._find_doc_url(soup, url)
                )

        return None

    def _extract_series(self, model: str) -> str:
        """Extract series name from model."""
        # Pattern: S12500, S5590, etc.
        match = re.match(r'(S\d{4,})', model)
        if match:
            return match.group(1)
        match = re.match(r'(S\d{3,})', model)
        if match:
            return match.group(1)
        return 'Unknown'

    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product full name from page."""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Try title
        title = soup.find('title')
        if title:
            text = title.get_text(strip=True)
            # Remove site suffix
            text = re.split(r'[-|]', text)[0].strip()
            return text

        return ''

    def _find_doc_url(self, soup: BeautifulSoup, product_url: str) -> Optional[str]:
        """Find link to hardware specifications document."""
        # Look for links to support/resources
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True).lower()
            if 'hardware' in text or 'specification' in text or 'support' in href:
                return urljoin(product_url, href)
        return None

    def save_discovery(self, filepath: str):
        """Save discovered products to JSON."""
        data = {
            'models': [asdict(m) for m in self.discovered_models],
            'series': [asdict(s) for s in self.discovered_series],
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved discovery to {filepath}")

    def load_discovery(self, filepath: str):
        """Load discovered products from JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.discovered_models = [ProductModel(**m) for m in data.get('models', [])]
        self.discovered_series = [ProductSeries(**s) for s in data.get('series', [])]
        logger.info(f"Loaded {len(self.discovered_models)} models from {filepath}")


if __name__ == '__main__':
    # Test
    mapper = H3CSiteMapper(delay=1.0)
    models = mapper.discover_campus_switches()
    print(f"Discovered {len(models)} models")
    for m in models[:5]:
        print(f"  - {m.model} ({m.category}): {m.url}")

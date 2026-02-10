#!/usr/bin/env python3
"""
Test script for table-extractor-agent skill
Usage: python test_extractor.py --url <url> --output <output.json>
"""
import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from crawler.html_fetcher import HTMLFetcher
from bs4 import BeautifulSoup
from skills.table_extractor_agent.scripts.extractor import extract_all_tables


def main():
    parser = argparse.ArgumentParser(description='Test table extraction')
    parser.add_argument('--url', required=True, help='URL to extract tables from')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--context', default='H3C switch specifications', help='Page context')
    args = parser.parse_args()

    print(f"Fetching {args.url}...")
    fetcher = HTMLFetcher(delay=1.0)
    html = fetcher.fetch(args.url)

    if not html:
        print("Failed to fetch page")
        return 1

    print(f"Extracting tables with LLM...")
    results = extract_all_tables(
        html_content=html,
        page_context=args.context,
        model="claude-sonnet-4-20250514"
    )

    print(f"Extracted data for {len(results)} models")
    for model in list(results.keys())[:5]:
        print(f"  - {model}")

    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Table Extractor Agent - End-to-end table extraction from product pages

Usage:
    python -m skills.table_extractor_agent.scripts.extractor --url <product_url> --output <output.json>
    
Example:
    python -m skills.table_extractor_agent.scripts.extractor \\
        --url "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Access/S5130/H3C_S5130S_EI/" \\
        --output s5130_specs.json
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from src.crawler.html_fetcher import HTMLFetcher
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
    from src.crawler.html_fetcher import HTMLFetcher

from bs4 import BeautifulSoup


def extract_all_tables_from_url(
    url: str,
    output_file: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514"
) -> Dict[str, Dict]:
    """
    Extract all tables from a product page URL.
    
    Args:
        url: Product page URL
        output_file: Optional output JSON file path
        model: LLM model to use
    
    Returns:
        Dictionary of {model_name: {parameter: value}}
    """
    print(f"🔗 Fetching page: {url}")
    
    # Step 1: Fetch the page
    fetcher = HTMLFetcher(delay=1.5, cache_dir='./data/raw')
    html = fetcher.fetch(url)
    
    if not html:
        raise Exception(f"Failed to fetch {url}")
    
    print(f"✅ Page fetched ({len(html)} characters)")
    
    # Step 2: Parse and find all tables
    soup = BeautifulSoup(html, 'lxml')
    tables = soup.find_all('table')
    
    print(f"📊 Found {len(tables)} tables")
    
    # Step 3: Extract data from each table using LLM
    all_data = {}
    
    for i, table in enumerate(tables):
        table_text = table.get_text()
        
        # Skip empty or navigation tables
        if len(table_text.strip()) < 100:
            continue
        
        print(f"\n📋 Processing table {i+1}/{len(tables)}...")
        
        # Use LLM to extract this table
        table_data = extract_single_table_with_llm(
            table_html=str(table),
            table_index=i,
            page_url=url,
            model=model
        )
        
        if table_data and 'data' in table_data:
            # Merge data into all_data
            for model_name, specs in table_data['data'].items():
                if model_name not in all_data:
                    all_data[model_name] = {}
                all_data[model_name].update(specs)
            
            print(f"   ✓ Extracted {len(table_data['data'])} models")
    
    print(f"\n✅ Total models extracted: {len(all_data)}")
    
    # Step 4: Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to: {output_file}")
    
    return all_data


def extract_single_table_with_llm(
    table_html: str,
    table_index: int,
    page_url: str,
    model: str = "claude-sonnet-4-20250514"
) -> Optional[Dict]:
    """
    Extract a single table using LLM analysis.
    
    In the actual implementation, this would call an LLM API.
    For now, this is a placeholder that shows the prompt structure.
    """
    # Clean the HTML for LLM processing
    cleaned_html = _clean_table_html(table_html)
    
    # Build the prompt
    prompt = _build_llm_prompt(cleaned_html, table_index, page_url)
    
    # TODO: In actual implementation, call LLM here
    # For demonstration, we return a structure showing what the LLM would do
    return {
        "table_index": table_index,
        "prompt": prompt,
        "note": "In actual implementation, this would be replaced with LLM response",
        "data": {}  # Would contain actual extracted data
    }


def _clean_table_html(html: str) -> str:
    """Clean HTML table for LLM processing."""
    # Remove style attributes
    html = re.sub(r'\s+style="[^"]*"', '', html)
    # Remove class attributes
    html = re.sub(r'\s+class="[^"]*"', '', html)
    # Remove id attributes
    html = re.sub(r'\s+id="[^"]*"', '', html)
    # Remove data-* attributes
    html = re.sub(r'\s+data-[a-z]+="[^"]*"', '', html)
    # Collapse whitespace
    html = re.sub(r'\s+', ' ', html)
    # Limit size
    return html[:8000]


def _build_llm_prompt(table_html: str, index: int, url: str) -> str:
    """Build the LLM extraction prompt."""
    return f"""You are a data extraction specialist. Parse the following HTML table from a product specification page.

Source URL: {url}
Table Index: {index}

HTML Table:
```html
{table_html}
```

Instructions:
1. Identify the table type:
   - hardware_specs: CPU, memory, ports, power, dimensions
   - software_features: VLAN, routing protocols, security, management
   - poe_power: POE power capacity, port counts per standard
   - performance: MAC table, routing table, forwarding rate
   - protocols: IEEE standards, RFC compliance
   - product_description: Port configurations in text

2. Handle merged cells (rowspan/colspan):
   - If a cell has rowspan="N", copy its value to N rows
   - If a cell has colspan="N", treat it as spanning N columns

3. For multi-model tables (Feature | Model1 | Model2 | ...):
   - Extract separate data dictionary for each model
   - Normalize parameter names to Chinese where appropriate

4. Parse port descriptions:
   - "24*10/100/1000Base-T" → {{"1000Base-T端口数": 24}}
   - "4*10G SFP+" → {{"SFP+端口数": 4}}
   - "4 (combo)" → indicate combo ports

5. For POE tables:
   - Extract power capacity in Watts
   - Parse port counts per standard (802.3af/at/bt)
   - Handle AC/DC configurations as separate entries

6. For software features:
   - List supported protocols/features
   - Note any quantitative limits (e.g., "4K VLANs")

Return JSON only:
{{
  "table_type": "hardware_specs|software_features|poe_power|performance|protocols|product_description",
  "models": ["model1", "model2", ...],
  "data": {{
    "model1": {{
      "参数名1": "值1",
      "参数名2": "值2"
    }},
    "model2": {{...}}
  }},
  "merged_cells_handled": true/false,
  "notes": "Any special handling or observations"
}}

JSON Output:"""


def main():
    parser = argparse.ArgumentParser(
        description='Extract tables from H3C product page',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract S5130 specs
  python extractor.py --url "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Access/S5130/H3C_S5130S_EI/" --output s5130.json
  
  # Extract S5590 specs
  python extractor.py --url "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Aggregation/S5500/H3C_S5590-EI/" --output s5590.json
        """
    )
    parser.add_argument('--url', required=True, help='Product page URL')
    parser.add_argument('--output', '-o', required=True, help='Output JSON file')
    parser.add_argument('--model', default='claude-sonnet-4-20250514', help='LLM model to use')
    
    args = parser.parse_args()
    
    try:
        results = extract_all_tables_from_url(
            url=args.url,
            output_file=args.output,
            model=args.model
        )
        
        # Print summary
        print(f"\n📊 Extraction Summary:")
        print(f"   Models: {len(results)}")
        for model_name in list(results.keys())[:5]:
            param_count = len(results[model_name])
            print(f"   - {model_name}: {param_count} parameters")
        if len(results) > 5:
            print(f"   ... and {len(results) - 5} more")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

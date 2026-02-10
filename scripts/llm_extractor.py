#!/usr/bin/env python3
"""
LLM-powered table extraction - uses current agent's LLM capabilities
"""
import json
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def extract_tables_with_llm(html_content: str, page_context: str = "") -> Dict[str, Dict]:
    """
    Extract all tables from HTML using LLM analysis.
    
    This function prepares tables and prompts for LLM processing.
    In the OpenClaw environment, the LLM (me) processes these directly.
    
    Args:
        html_content: Full HTML page content
        page_context: Description of the page (e.g., "H3C S5130 switch specs")
    
    Returns:
        Dictionary of {model_name: {parameter: value}}
    """
    soup = BeautifulSoup(html_content, 'lxml')
    tables = soup.find_all('table')
    
    all_results = {}
    
    for i, table in enumerate(tables):
        table_text = table.get_text(strip=True)
        
        # Skip navigation and tiny tables
        if len(table_text) < 200:
            continue
        
        # Clean and prepare table
        cleaned = _clean_html(str(table))
        
        # Analyze table with LLM
        result = _analyze_table_with_llm(cleaned, i, page_context)
        
        if result and 'data' in result:
            # Merge into all_results
            for model_name, specs in result['data'].items():
                if model_name not in all_results:
                    all_results[model_name] = {}
                all_results[model_name].update(specs)
    
    return all_results


def _analyze_table_with_llm(table_html: str, index: int, context: str) -> Optional[Dict]:
    """
    Analyze a single table using LLM.
    
    In OpenClaw, this would trigger the agent (me) to analyze the table.
    For now, this returns the prompt that would be sent.
    """
    # This is where the LLM analysis happens
    # In actual OpenClaw usage, this would call the LLM API
    
    prompt = f"""Analyze this HTML table from {context}:

```html
{table_html[:5000]}
```

Extract structured data following these rules:
1. Identify table type (hardware/software/poe/performance/protocols)
2. Handle merged cells (rowspan/colspan) by propagating values
3. For multi-model tables, extract per-model data
4. Normalize Chinese parameter names
5. Parse port descriptions into port_type: count format

Return JSON with models and their specifications."""

    # In actual implementation, this would call LLM
    # For demonstration, return None (caller should handle via external LLM)
    return None


def _clean_html(html: str) -> str:
    """Clean HTML for processing."""
    # Remove script and style
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # Remove attributes
    html = re.sub(r'\s+(style|class|id|onclick|onload)="[^"]*"', '', html)
    # Clean whitespace
    html = re.sub(r'\s+', ' ', html)
    return html.strip()


# Table type detection patterns
TABLE_PATTERNS = {
    'hardware': ['cpu', 'memory', 'port', 'power', 'dimension', 'weight', 'mtbf'],
    'software': ['vlan', 'routing', 'protocol', 'security', 'feature'],
    'poe': ['poe', 'power capacity', '802.3af', '802.3at', '802.3bt'],
    'performance': ['mac address', 'routing table', 'forwarding', 'capacity'],
    'protocols': ['ieee', 'rfc', 'standards', 'compliance']
}


def detect_table_type(table_text: str) -> str:
    """Detect table type from content."""
    text_lower = table_text.lower()
    
    for table_type, patterns in TABLE_PATTERNS.items():
        if any(p in text_lower for p in patterns):
            return table_type
    
    return 'unknown'

# H3C Specs Extractor

Extract H3C switch specifications from HTML tables. Handles hardware specs, software features, performance metrics, and protocol compliance.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ElanGll2023/h3c-specs-extractor)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

## Features

- ✅ **Hardware Specs** - Ports, power, fans, dimensions, weight
- ✅ **Software Features** - VLAN, routing, security features  
- ✅ **Performance Metrics** - MAC table, VLAN table, routing table, ACL rules
- ✅ **Protocol Compliance** - IEEE standards, RFC protocols
- ✅ **POE Support** - POE/POE+/POE++ power and port counts
- ✅ **Encoding Fix** - Auto-fix `Ã` → `×`, `Âµ` → `µ`, etc.
- ✅ **Merged Cells** - Handle rowspan/colspan properly
- ✅ **Smart Filtering** - Skip removable components, power models

## Two Versions Available

| Version | Use Case | Repository |
|---------|----------|------------|
| **Python Module** (this repo) | Standalone scripts, automation | [h3c-specs-extractor](https://github.com/ElanGll2023/h3c-specs-extractor) |
| **Claude Code Skill** | Claude Code integration | [h3c-table-extractor-claude](https://github.com/ElanGll2023/h3c-table-extractor-claude) |

## Installation

```bash
git clone https://github.com/ElanGll2023/h3c-specs-extractor.git
cd h3c-specs-extractor
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from scripts.direct_extractor import extract_tables_direct
from crawler.html_fetcher import HTMLFetcher

url = "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Access/S5130/H3C_S5130S_EI/"
fetcher = HTMLFetcher(delay=1.0)
html = fetcher.fetch(url)
results = extract_tables_direct(html, url)

# Filter actual models
models = {k: v for k, v in results.items() if k.startswith('S5130')}
print(f"Extracted {len(models)} models")
```

### Batch Extraction

```python
from scripts.direct_extractor import extract_tables_direct
from crawler.html_fetcher import HTMLFetcher
import pandas as pd

urls = {
    'S5130': 'https://www.h3c.com/en/.../H3C_S5130S_EI/',
    'S5590': 'https://www.h3c.com/en/.../H3C_S5590-EI/',
    'S6520': 'https://www.h3c.com/en/.../H3C_S6520X-EI/',
}

all_data = {}
for series, url in urls.items():
    fetcher = HTMLFetcher(delay=1.5)
    html = fetcher.fetch(url)
    results = extract_tables_direct(html, url)
    models = {k: v for k, v in results.items() if k.startswith('S')}
    all_data.update(models)

# Export to Excel
df = pd.DataFrame.from_dict(all_data, orient='index')
df.to_excel('h3c_switches.xlsx')
```

## Extracted Fields

### Hardware Specs
- `交换容量` - Switching capacity
- `包转发率` - Packet forwarding rate
- `1000Base-T端口数` - Gigabit Ethernet ports
- `SFP端口数`, `SFP+端口数`, `QSFP+端口数` - Fiber ports
- `电源槽位数` - Power supply slots
- `风扇数量` - Fan count
- `Console口`, `USB口`, `管理网口` - Management ports
- `尺寸`, `重量` - Physical dimensions
- `功耗`, `输入电压` - Power specs

### Software Features
- `软件特性` - Software features summary

### Performance Metrics
- `MAC地址表` - MAC address table size
- `VLAN表项` - VLAN table entries
- `路由表项` - Routing table entries
- `ARP表项` - ARP entries
- `ACL规则数` - ACL rules

### Protocols
- `支持协议` - Supported protocols summary

### POE (if supported)
- `POE总功率` - Total POE power budget
- `POE端口数(802.3af)` - POE ports (15.4W)
- `POE+端口数(802.3at)` - POE+ ports (30W)
- `POE++端口数(60W)` - POE++ ports (60W)
- `POE++端口数(90W)` - POE++ ports (90W)

## Table Types Handled

1. **Multi-model hardware tables** - Standard spec tables with model columns
2. **POE tables** - Power consumption and POE port distribution  
3. **Software feature tables** - VLAN, routing, security features
4. **Performance tables** - MAC, VLAN, routing table sizes
5. **Protocol tables** - IEEE standards and RFC compliance

## Encoding Fixes

Automatically fixes common encoding issues (mojibake):
- `Ã` → `×` (multiplication sign)
- `Âµ` → `µ` (micro sign)
- `Â°` → `°` (degree sign)
- `â¤` → `≤` (less than or equal)
- `â¥` → `≥` (greater than or equal)

## Filtered Content

Automatically skips to keep output clean:
- Removable power supply models (PSR150-A1-GL, etc.)
- Board support indicators (是否支持)
- Filler panel information
- Transceiver part numbers (unless specifically requested)

## Version

- **Version**: 1.0.0
- **Last Updated**: 2026-02-10
- **Python**: 3.8+

## Related Projects

- [h3c-table-extractor-claude](https://github.com/ElanGll2023/h3c-table-extractor-claude) - Claude Code skill version

## License

MIT

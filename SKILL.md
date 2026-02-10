---
name: h3c-specs-extractor
description: Extract H3C switch specifications from HTML tables. Direct Python module - no Claude Code required. Handles hardware specs, software features, performance metrics, and protocol compliance. Filters out removable components.
---

# H3C Specs Extractor

**✅ 立即可用** - 直接 Python 模块，无需 Claude Code

## 功能

- ✅ 提取硬件规格（端口、电源、风扇、尺寸）
- ✅ 提取软件特性（VLAN、路由、安全）
- ✅ 提取性能参数（MAC表、VLAN表、路由表）
- ✅ 提取标准协议（IEEE、RFC）
- ✅ 处理合并单元格（rowspan/colspan）
- ✅ 自动修复编码乱码（`Ã` → `×`）
- ✅ 过滤冗余信息（可移除部件、电源型号等）

## 使用方法

### 基础用法

```python
from skills.h3c_specs_extractor.scripts.direct_extractor import extract_tables_direct
from src.crawler.html_fetcher import HTMLFetcher

url = "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Access/S5130/H3C_S5130S_EI/"
fetcher = HTMLFetcher(delay=1.0)
html = fetcher.fetch(url)
results = extract_tables_direct(html, url)

# 过滤实际型号
models = {k: v for k, v in results.items() if k.startswith('S5130')}
print(f"Extracted {len(models)} models")
```

### 批量提取多个系列

```python
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
    print(f"{series}: {len(models)} models")

# 导出 Excel
import pandas as pd
df = pd.DataFrame.from_dict(all_data, orient='index')
df.to_excel('h3c_switches.xlsx')
```

## 提取的字段

### 硬件规格
- `交换容量` - Switching capacity
- `包转发率` - Packet forwarding rate
- `1000Base-T端口数` - Gigabit Ethernet ports
- `SFP端口数`, `SFP+端口数`, `QSFP+端口数` - Fiber ports
- `电源槽位数` - Power supply slots
- `风扇数量` - Fan count
- `Console口`, `USB口`, `管理网口` - Management ports
- `尺寸`, `重量` - Physical dimensions
- `功耗`, `输入电压` - Power specs

### 软件特性
- `软件特性` - Software features summary

### 性能参数
- `MAC地址表` - MAC address table size
- `VLAN表项` - VLAN table entries
- `路由表项` - Routing table entries
- `ARP表项` - ARP entries
- `ACL规则数` - ACL rules

### 协议支持
- `支持协议` - Supported protocols summary

### POE (如果支持)
- `POE总功率` - Total POE power budget
- `POE端口数(802.3af)` - POE ports (15.4W)
- `POE+端口数(802.3at)` - POE+ ports (30W)
- `POE++端口数(60W)` - POE++ ports (60W)
- `POE++端口数(90W)` - POE++ ports (90W)

## 过滤掉的字段

以下内容会被自动过滤：
- 可移除部件型号（Removable power supplies）
- 电源模块具体型号（PSR150-A1-GL 等）
- 板卡支持状态（是否支持）
- 填充面板信息（Filler panel）

## 编码修复

自动修复 HTML 实体乱码：
- `Ã` → `×`
- `Âµ` → `µ`
- `Â°` → `°`
- `â¤` → `≤`

## 命令行使用

```bash
python -m skills.h3c_specs_extractor.scripts.extractor \
    --url "https://www.h3c.com/en/.../H3C_S5130S_EI/" \
    --output s5130_specs.json
```

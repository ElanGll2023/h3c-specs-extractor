#!/usr/bin/env python3
"""
Robust Universal Extractor - 演示脚本
展示新的视觉结构分析功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.robust_extractor import RobustUniversalExtractor, extract_robust
from core.visual_analyzer import VisualStructureAnalyzer


def demo_visual_analysis(url: str = None):
    """演示视觉结构分析"""
    from crawler.html_fetcher import HTMLFetcher
    
    if not url:
        url = "https://www.h3c.com/en/Products_and_Solutions/InterConnect/Switches/Products/Campus_Network/Access/S5130/H3C_S5130S_EI/"
    
    print("=" * 70)
    print("🎉 健壮版通用提取器 - 视觉结构分析演示")
    print("=" * 70)
    print(f"\n📍 目标URL: {url}")
    print("\n🔄 正在获取页面...")
    
    fetcher = HTMLFetcher(delay=1.5)
    html = fetcher.fetch(url)
    
    print("✅ 页面获取成功")
    print("\n" + "-" * 70)
    
    # 1. 执行完整提取流程
    print("\n🔍 执行完整提取分析流程...\n")
    
    extractor = RobustUniversalExtractor()
    result = extractor.extract_with_analysis(html, url)
    
    # 2. 显示分析报告
    print(extractor.get_detailed_report())
    
    # 3. 显示提取结果摘要
    print("\n📊 提取结果摘要:")
    print("-" * 70)
    
    data = result['data']
    print(f"✅ 成功提取 {len(data)} 个型号")
    
    if data:
        sample_model = list(data.keys())[0]
        print(f"\n📋 样本型号: {sample_model}")
        sample_data = data[sample_model]
        
        print(f"   字段数量: {len(sample_data)}")
        print(f"   主要字段:")
        for key in list(sample_data.keys())[:10]:
            value = sample_data[key]
            display_value = str(value)[:40] + "..." if len(str(value)) > 40 else str(value)
            print(f"      - {key}: {display_value}")
    
    # 4. 显示改进建议
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n💡 发现 {len(recommendations)} 条改进建议:")
        print("-" * 70)
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. [{rec['priority'].upper()}] {rec['category']}")
            print(f"   {rec['message']}")
            print(f"   建议操作: {rec.get('action', 'N/A')}")
            print()
    
    # 5. 生成配置模板
    print("\n📝 生成配置模板片段:")
    print("-" * 70)
    config_template = extractor.generate_config_template(html, url)
    print(config_template[:1500] + "\n... (truncated)")
    
    print("\n" + "=" * 70)
    print("✨ 演示完成!")
    print("=" * 70)
    print("\n使用说明:")
    print("  1. 如需交互式配置: extract_robust(html, url, interactive=True)")
    print("  2. 仅分析页面: analyze_page(html, url)")
    print("  3. 生成配置: extractor.generate_config_template(html, url)")


def demo_compare_profiles():
    """演示不同配置的对比"""
    print("\n" + "=" * 70)
    print("📚 可用配置文件对比")
    print("=" * 70)
    
    from core.rule_engine import get_rule_engine
    
    engine = get_rule_engine("config")
    profiles = engine.list_profiles()
    
    print(f"\n发现 {len(profiles)} 个配置文件:\n")
    
    for p in profiles:
        print(f"  📄 {p['name']}")
        print(f"     品牌: {p['brand']}")
        print(f"     类型: {p['type']} ({p['sub_type']})")
        print(f"     版本: {p['version']}")
        print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Robust Universal Extractor Demo')
    parser.add_argument('--url', '-u', help='Target URL to analyze')
    parser.add_argument('--list-profiles', '-l', action='store_true', 
                       help='List available profiles')
    
    args = parser.parse_args()
    
    if args.list_profiles:
        demo_compare_profiles()
    else:
        demo_visual_analysis(args.url)


if __name__ == "__main__":
    main()

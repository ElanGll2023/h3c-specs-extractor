"""
Universal Product Specs Extractor
可累加的配置驱动产品规格提取器
"""

from .rule_engine import RuleEngine, ProductProfile, ExtractionRule, get_rule_engine
from .page_analyzer import PageAnalyzer, PageAnalysisReport
from .universal_extractor import UniversalExtractor, extract_specs
from .config_wizard import ConfigurationWizard

__version__ = "2.0.0"
__all__ = [
    'RuleEngine',
    'ProductProfile',
    'ExtractionRule',
    'PageAnalyzer',
    'PageAnalysisReport',
    'UniversalExtractor',
    'extract_specs',
    'ConfigurationWizard',
    'get_rule_engine',
]

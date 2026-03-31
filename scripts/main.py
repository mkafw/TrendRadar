#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar-Issues 主程序
整合 RSS 文章和热搜抓取，通过 AI 分析后保存到 GitHub Issues
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logger.remove()
logger.add(
    "logs/trendradar_{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(sys.stdout, level="INFO")

class TrendRadarIssues:
    def __init__(self):
        self.config = self.load_config()
        self.source_type = os.getenv("SOURCE_TYPE", "both")
        
        logger.info(f"TrendRadar-Issues 初始化完成，数据源类型：{self.source_type}")
        
    def load_config(self):
        """加载配置文件"""
        import yaml
        config_path = Path("config/config.yaml")
        if not config_path.exists():
            logger.error("配置文件不存在：config/config.yaml")
            sys.exit(1)
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        logger.info(f"配置加载成功")
        return config
    
    def load_keywords(self):
        """加载关键词配置"""
        keywords = {
            'normal': [],
            'required': [],
            'excluded': [],
            'global_filter': []
        }
        
        keyword_file = Path("config/frequency_words.txt")
        if not keyword_file.exists():
            logger.warning("关键词配置文件不存在")
            return keywords
            
        current_section = 'normal'
        
        with open(keyword_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    if not line:
                        current_section = 'normal'
                    continue
                
                if line == '[GLOBAL_FILTER]':
                    current_section = 'global_filter'
                    continue
                
                if line.startswith('+'):
                    keywords['required'].append(line[1:])
                elif line.startswith('!'):
                    keywords['excluded'].append(line[1:])
                elif line.startswith('@'):
                    continue
                else:
                    if current_section == 'global_filter':
                        keywords['global_filter'].append(line)
                    else:
                        keywords['normal'].append(line)
                        
        logger.info(f"关键词加载完成：普通={len(keywords['normal'])}, 必须={len(keywords['required'])}, 排除={len(keywords['excluded'])}, 全局={len(keywords['global_filter'])}")
        return keywords
    
    def filter_content(self, title, content, keywords):
        """内容过滤"""
        # 全局过滤
        for word in keywords['global_filter']:
            if word in title or word in content:
                return False, "global_filter"
        
        # 排除词过滤
        for word in keywords['excluded']:
            if word in title or word in content:
                return False, "excluded"
        
        # 必须词检查
        if keywords['required']:
            for word in keywords['required']:
                if word not in title and word not in content:
                    return False, "missing_required"
        
        # 普通词匹配
        if keywords['normal']:
            matched = False
            for word in keywords['normal']:
                if word in title or word in content:
                    matched = True
                    break
            if not matched:
                return False, "no_match"
        
        return True, "passed"
    
    async def run(self):
        """主执行流程"""
        logger.info("=" * 60)
        logger.info("TrendRadar-Issues 开始执行")
        logger.info("=" * 60)
        
        keywords = self.load_keywords()
        all_items = []
        
        # 1. 抓取 RSS 文章
        if self.source_type in ['rss', 'both'] and self.config['rss']['enabled']:
            logger.info("\n【RSS 抓取】开始...")
            from scripts.fetch_rss import RSSFetcher
            rss_fetcher = RSSFetcher(self.config)
            rss_items = await rss_fetcher.fetch()
            logger.info(f"RSS 抓取完成，共 {len(rss_items)} 篇文章")
            
            # 过滤和分析
            for item in rss_items:
                passed, reason = self.filter_content(
                    item.get('title', ''),
                    item.get('content', ''),
                    keywords
                )
                
                if not passed:
                    logger.debug(f"RSS 过滤：{item.get('title')[:30]}... - {reason}")
                    continue
                
                # AI 分析
                if self.config['ai']['enabled']:
                    from scripts.ai_analyze import AIAnalyzer
                    ai_analyzer = AIAnalyzer(self.config)
                    analysis = await ai_analyzer.analyze(item)
                    item.update(analysis)
                    
                    if item.get('score', 0) < self.config['ai']['min_score']:
                        logger.debug(f"RSS 分数过低：{item.get('title')[:30]}... - {item.get('score')}分")
                        continue
                
                item['source_type'] = 'rss'
                all_items.append(item)
        
        # 2. 抓取热搜
        if self.source_type in ['hotspots', 'both'] and self.config['hotspots']['enabled']:
            logger.info("\n【热搜抓取】开始...")
            from scripts.fetch_hotspots import HotspotsFetcher
            hotspots_fetcher = HotspotsFetcher(self.config)
            hotspots_items = await hotspots_fetcher.fetch()
            logger.info(f"热搜抓取完成，共 {len(hotspots_items)} 条")
            
            # 过滤和分析
            for item in hotspots_items:
                passed, reason = self.filter_content(
                    item.get('title', ''),
                    item.get('content', ''),
                    keywords
                )
                
                if not passed:
                    logger.debug(f"热搜过滤：{item.get('title')[:30]}... - {reason}")
                    continue
                
                if self.config['ai']['enabled']:
                    from scripts.ai_analyze import AIAnalyzer
                    ai_analyzer = AIAnalyzer(self.config)
                    analysis = await ai_analyzer.analyze(item)
                    item.update(analysis)
                    
                    if item.get('score', 0) < self.config['ai']['min_score']:
                        logger.debug(f"热搜分数过低：{item.get('title')[:30]}... - {item.get('score')}分")
                        continue
                
                item['source_type'] = 'hotspot'
                all_items.append(item)
        
        logger.info(f"\n过滤后剩余：{len(all_items)} 条")
        
        # 3. 去重检测
        if self.config['filter']['duplicate_check']:
            from scripts.create_issues import IssueManager
            issue_manager = IssueManager(self.config)
            all_items = await issue_manager.remove_duplicates(all_items)
            logger.info(f"去重后剩余：{len(all_items)} 条")
        
        # 4. 创建 GitHub Issues
        if self.config['github']['auto_create_issues'] and all_items:
            logger.info("\n【创建 Issues】开始...")
            from scripts.create_issues import IssueManager
            issue_manager = IssueManager(self.config)
            created_count = await issue_manager.create_issues(all_items)
            logger.info(f"Issues 创建完成，共创建 {created_count} 个")
        
        # 5. 保存记录
        self.save_record(all_items)
        
        logger.info("\n" + "=" * 60)
        logger.info("TrendRadar-Issues 执行完成")
        logger.info("=" * 60)
        
        return len(all_items)
    
    def save_record(self, items):
        """保存处理记录"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        record_file = output_dir / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'source_type': self.source_type,
            'total_items': len(items),
            'items': items
        }
        
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
            
        logger.info(f"处理记录已保存：{record_file}")


if __name__ == "__main__":
    import asyncio
    
    trendradar = TrendRadarIssues()
    result = asyncio.run(trendradar.run())
    
    sys.exit(0 if result > 0 else 1)

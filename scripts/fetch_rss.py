#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS 抓取模块
解析 OPML 文件，抓取 BestBlogs 的 400+ RSS 订阅源
"""

import feedparser
import aiohttp
from datetime import datetime, timezone
from pathlib import Path
from loguru import logger
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


class RSSFetcher:
    def __init__(self, config):
        self.config = config
        self.opml_file = config['rss']['opml_file']
        self.user_agent = config['rss']['user_agent']
        self.max_articles = config['rss']['max_articles_per_run']
        
    def parse_opml(self):
        """解析 OPML 文件，获取所有 RSS 订阅源"""
        opml_path = Path(self.opml_file)
        if not opml_path.exists():
            logger.error(f"OPML 文件不存在：{opml_path}")
            return []
        
        tree = ET.parse(opml_path)
        root = tree.getroot()
        
        feeds = []
        
        def find_outlines(element):
            for child in element:
                if child.tag == 'outline':
                    xml_url = child.get('xmlUrl')
                    if xml_url:
                        feeds.append({
                            'title': child.get('title') or child.get('text', 'Unknown'),
                            'url': xml_url
                        })
                    find_outlines(child)
        
        find_outlines(root)
        logger.info(f"解析 OPML 完成，共 {len(feeds)} 个订阅源")
        return feeds
    
    async def fetch_single_feed(self, session, feed_url, feed_title):
        """抓取单个 RSS 订阅源"""
        try:
            headers = {'User-Agent': self.user_agent}
            async with session.get(feed_url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.debug(f"RSS 抓取失败 {feed_title}: HTTP {response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:5]:  # 每个订阅源最多取 5 篇
                    article = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', entry.get('updated', '')),
                        'source': feed_title,
                        'source_type': 'rss',
                        'content': '',
                        'summary': entry.get('summary', '')
                    }
                    
                    # 提取全文
                    if hasattr(entry, 'content') and entry.content:
                        article['content'] = entry.content[0].value
                    elif article['summary']:
                        article['content'] = article['summary']
                    
                    # 清理 HTML 标签
                    if article['content']:
                        soup = BeautifulSoup(article['content'], 'html.parser')
                        article['content'] = soup.get_text(separator=' ', strip=True)[:5000]
                    
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.debug(f"RSS 抓取错误 {feed_title}: {str(e)}")
            return []
    
    async def fetch(self):
        """主抓取方法"""
        feeds = self.parse_opml()
        if not feeds:
            return []
        
        all_articles = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for feed in feeds:
                task = self.fetch_single_feed(session, feed['url'], feed['title'])
                tasks.append(task)
            
            import asyncio
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
        
        # 按发布时间排序
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # 限制数量
        return all_articles[:self.max_articles]

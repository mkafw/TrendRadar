#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热搜抓取模块
调用 newsnow API 获取各平台热搜（TrendRadar 核心功能）
"""

import aiohttp
from datetime import datetime
from loguru import logger


class HotspotsFetcher:
    def __init__(self, config):
        self.config = config
        self.platforms = config['hotspots']['platforms']
        self.max_items = config['hotspots']['max_items_per_platform']
        self.api_base = "https://newsnow.busiyi.world/api/v1"
    
    async def fetch_platform(self, session, platform):
        """抓取单个平台的热搜"""
        try:
            url = f"{self.api_base}/hotlist?source={platform['id']}&limit={self.max_items}"
            
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    logger.debug(f"热搜抓取失败 {platform['name']}: HTTP {response.status}")
                    return []
                
                data = await response.json()
                items = []
                hotlist = data.get('data', {}).get('hot_list', [])
                
                for item in hotlist:
                    items.append({
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'rank': item.get('rank', 0),
                        'hot_value': item.get('hot_value', ''),
                        'source': platform['name'],
                        'source_type': 'hotspot',
                        'content': item.get('title', ''),
                        'summary': '',
                        'published': datetime.now().isoformat()
                    })
                
                logger.debug(f"平台 {platform['name']} 抓取 {len(items)} 条")
                return items
                
        except Exception as e:
            logger.debug(f"热搜抓取错误 {platform['name']}: {str(e)}")
            return []
    
    async def fetch(self):
        """主抓取方法"""
        all_items = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for platform in self.platforms:
                task = self.fetch_platform(session, platform)
                tasks.append(task)
            
            import asyncio
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_items.extend(result)
        
        logger.info(f"热搜抓取完成，共 {len(all_items)} 条")
        return all_items

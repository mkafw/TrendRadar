#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Issues 管理模块
创建、更新、关闭 Issues
"""

import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class IssueManager:
    def __init__(self, config):
        self.config = config
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPOSITORY", "")
        
        if not self.token or not self.repo:
            logger.warning("GITHUB_TOKEN 或 GITHUB_REPOSITORY 未配置")
            self.github = None
        else:
            from github import Github
            self.github = Github(self.token)
            self.repo_obj = self.github.get_repo(self.repo)
            logger.info(f"GitHub 客户端初始化成功：{self.repo}")
            self._init_labels()
    
    def _init_labels(self):
        """初始化 Issue Labels"""
        labels_config = self.config['github']['labels']
        
        for label_cfg in labels_config:
            try:
                self.repo_obj.get_label(label_cfg['name'])
            except:
                self.repo_obj.create_label(
                    name=label_cfg['name'],
                    color=label_cfg['color'],
                    description=label_cfg.get('description', '')
                )
                logger.info(f"创建 Label: {label_cfg['name']}")
    
    def _generate_issue_id(self, item):
        """生成内容的唯一标识（用于去重）"""
        content = f"{item.get('title', '')}{item.get('link', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def remove_duplicates(self, items):
        """去重检测"""
        if not self.github:
            return items
        
        window_hours = self.config['filter']['duplicate_window_hours']
        since = datetime.now() - timedelta(hours=window_hours)
        
        existing_ids = set()
        try:
            issues = self.repo_obj.get_issues(state='all', since=since)
            for issue in issues:
                if issue.title.startswith('['):
                    end_idx = issue.title.find(']')
                    if end_idx > 0:
                        existing_ids.add(issue.title[1:end_idx])
        except Exception as e:
            logger.error(f"去重检测失败：{str(e)}")
        
        unique_items = []
        for item in items:
            item_id = self._generate_issue_id(item)
            if item_id not in existing_ids:
                unique_items.append(item)
            else:
                logger.debug(f"检测到重复：{item.get('title')[:30]}...")
        
        return unique_items
    
    def _get_score_label(self, score):
        """根据分数获取 Label"""
        if score >= 90:
            return "ai-score-90+"
        elif score >= 80:
            return "ai-score-80+"
        elif score >= 70:
            return "ai-score-70+"
        return None
    
    async def create_issues(self, items):
        """批量创建 Issues"""
        if not self.github:
            logger.warning("GitHub 客户端未初始化，跳过 Issues 创建")
            return 0
        
        created_count = 0
        
        for item in items:
            try:
                issue_id = self._generate_issue_id(item)
                title = f"[{issue_id}] {item.get('title', '')[:150]}"
                body = self._build_issue_body(item, issue_id)
                
                issue = self.repo_obj.create_issue(
                    title=title,
                    body=body,
                    labels=[]
                )
                
                # 添加 Labels
                labels = []
                if item.get('source_type') == 'rss':
                    labels.append("rss-article")
                else:
                    labels.append("hotspot")
                
                score_label = self._get_score_label(item.get('score', 0))
                if score_label:
                    labels.append(score_label)
                
                if item.get('score', 0) >= 85:
                    labels.append("featured")
                
                if labels:
                    issue.set_labels(labels)
                
                created_count += 1
                logger.info(f"创建 Issue: {title[:50]}...")
                
            except Exception as e:
                logger.error(f"创建 Issue 失败：{str(e)}")
        
        return created_count
    
    def _build_issue_body(self, item, issue_id):
        """构建 Issue 正文"""
        score = item.get('score', 0)
        
        if score >= 90:
            score_emoji = "🏆"
        elif score >= 80:
            score_emoji = "⭐"
        elif score >= 70:
            score_emoji = "✅"
        else:
            score_emoji = "📄"
        
        body = f"""
## 📊 AI 评分 {score_emoji} {score} 分

### 📝 一句话总结
{item.get('one_sentence', '暂无')}

### 📄 摘要
{item.get('summary', '暂无摘要')}

### 🔖 关键词
{', '.join(item.get('keywords', ['暂无']))}

---

## 🔗 原文链接
{item.get('link', '无链接')}

## 📰 来源
{item.get('source', '未知')} | {item.get('source_type', 'unknown')}

## 🕐 发布时间
{item.get('published', '未知')}

---

*此 Issue 由 TrendRadar-Issues 自动创建 | ID: `{issue_id}`*
"""
        return body
    
    async def close_old_issues(self):
        """关闭过期 Issues"""
        if not self.github:
            return 0
        
        keep_days = self.config['filter']['keep_days']
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        closed_count = 0
        try:
            issues = self.repo_obj.get_issues(state='open')
            
            for issue in issues:
                if not issue.title.startswith('['):
                    continue
                
                if issue.created_at.replace(tzinfo=None) < cutoff_date:
                    issue.add_to_labels('auto-close')
                    issue.edit(state='closed')
                    closed_count += 1
                    logger.info(f"关闭过期 Issue: {issue.title[:50]}...")
                    
        except Exception as e:
            logger.error(f"关闭 Issues 失败：{str(e)}")
        
        return closed_count

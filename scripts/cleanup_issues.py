#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Issues 清理模块
定期关闭过期 Issues
"""

import os
from datetime import datetime, timedelta
from loguru import logger
from github import Github
import yaml


def main():
    """主函数"""
    with open("config/config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    
    if not token or not repo_name:
        logger.error("GitHub 配置不完整")
        return
    
    github = Github(token)
    repo = github.get_repo(repo_name)
    
    keep_days = config['filter']['keep_days']
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    logger.info(f"开始清理过期 Issues，保留天数：{keep_days}天，截止日期：{cutoff_date}")
    
    closed_count = 0
    
    try:
        # 确保 auto-close 标签存在
        try:
            auto_close_label = repo.get_label("auto-close")
        except:
            auto_close_label = repo.create_label(
                name="auto-close",
                color="B60205",
                description="自动关闭的过期 Issue"
            )
            logger.info("创建 auto-close 标签")
        
        # 获取所有开放的 Issues
        issues = repo.get_issues(state='open')
        
        for issue in issues:
            # 只处理自动创建的 Issues
            if not issue.title.startswith('['):
                continue
            
            # 检查创建时间
            if issue.created_at.replace(tzinfo=None) < cutoff_date:
                try:
                    issue.add_to_labels('auto-close')
                    issue.edit(state='closed')
                    closed_count += 1
                    logger.info(f"关闭过期 Issue #{issue.number}: {issue.title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"关闭 Issue 失败 #{issue.number}: {str(e)}")
        
        logger.info(f"清理完成，共关闭 {closed_count} 个过期 Issues")
        
    except Exception as e:
        logger.error(f"清理过程出错：{str(e)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件汇总发送模块
发送每日内容汇总到邮箱
"""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger


class EmailSender:
    def __init__(self, config):
        self.config = config
        
        self.from_email = os.getenv("EMAIL_FROM", "")
        self.password = os.getenv("EMAIL_PASSWORD", "")
        self.to_email = os.getenv("EMAIL_TO", "")
        
        # 自动识别 SMTP
        email_domain = self.from_email.split('@')[-1].lower() if self.from_email else ''
        smtp_map = {
            'gmail.com': ('smtp.gmail.com', 587),
            'qq.com': ('smtp.qq.com', 465),
            '163.com': ('smtp.163.com', 465),
            '126.com': ('smtp.126.com', 465),
            'outlook.com': ('smtp-mail.outlook.com', 587),
        }
        
        self.smtp_server, self.smtp_port = smtp_map.get(email_domain, ('', 0))
        
        if not all([self.from_email, self.password, self.to_email]):
            logger.warning("邮件配置不完整，跳过邮件发送")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"邮件发送初始化成功：{self.from_email} -> {self.to_email}")
    
    def _build_email_html(self, items, period='daily'):
        """构建邮件 HTML 内容"""
        period_text = "每日" if period == 'daily' else "每周"
        date_str = datetime.now().strftime("%Y年%m月%d日")
        
        # 按来源分组
        grouped = {}
        for item in items:
            source = item.get('source', '未知')
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(item)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 20px; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 15px; }}
        .item {{ background: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .item-title {{ font-size: 16px; font-weight: bold; margin-bottom: 8px; }}
        .item-title a {{ color: #333; text-decoration: none; }}
        .item-title a:hover {{ color: #667eea; }}
        .item-meta {{ font-size: 12px; color: #666; margin-bottom: 8px; }}
        .item-summary {{ font-size: 14px; color: #555; }}
        .score {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .score-90 {{ background: #0E8A16; color: white; }}
        .score-80 {{ background: #53B358; color: white; }}
        .score-70 {{ background: #AED581; color: #333; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 TrendRadar {period_text}汇总</h1>
            <p>{date_str} | 共 {len(items)} 条精选内容</p>
        </div>
"""
        
        for source, source_items in grouped.items():
            html += f"""
        <div class="section">
            <div class="section-title">📍 {source} ({len(source_items)}条)</div>
"""
            
            for item in source_items[:10]:
                score = item.get('score', 0)
                score_class = f"score-{int(score/10)*10}" if score >= 70 else "score-70"
                
                html += f"""
            <div class="item">
                <div class="item-title">
                    <a href="{item.get('link', '#')}">{item.get('title', '无标题')}</a>
                </div>
                <div class="item-meta">
                    <span class="score {score_class}">AI 评分：{score}</span>
                    {' | 🔖 ' + ', '.join(item.get('keywords', [])[:3]) if item.get('keywords') else ''}
                </div>
                <div class="item-summary">
                    {item.get('summary', item.get('one_sentence', '暂无摘要'))[:150]}...
                </div>
            </div>
"""
            
            html += """
        </div>
"""
        
        html += f"""
        <div class="footer">
            <p>此邮件由 TrendRadar-Issues 自动发送</p>
            <p>GitHub: https://github.com/{os.getenv('GITHUB_REPOSITORY', '')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def send(self, items, period='daily'):
        """发送邮件"""
        if not self.enabled or not items:
            logger.warning("邮件发送条件不满足，跳过")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = f"[TrendRadar] {period == 'daily' and '每日' or '每周'}汇总 - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_content = self._build_email_html(items, period)
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.from_email, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"邮件发送成功：{len(items)} 条内容 -> {self.to_email}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败：{str(e)}")
            return False


def main():
    """主函数"""
    import yaml
    from github import Github
    
    with open("config/config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    sender = EmailSender(config)
    
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY", "")
    
    if not token or not repo_name:
        logger.error("GitHub 配置不完整")
        return
    
    github = Github(token)
    repo = github.get_repo(repo_name)
    
    today = datetime.now().date()
    issues = []
    
    for issue in repo.get_issues(state='all'):
        if issue.created_at.date() == today:
            if issue.body:
                import re
                score = 70
                if "AI 评分" in issue.body:
                    match = re.search(r'AI 评分.*?(\d+) 分', issue.body)
                    if match:
                        score = int(match.group(1))
                
                link = ""
                if "原文链接" in issue.body:
                    link_match = re.search(r'\]\((https?://[^\)]+)\)', issue.body)
                    if link_match:
                        link = link_match.group(1)
                
                issues.append({
                    'title': issue.title.split(']')[-1].strip() if ']' in issue.title else issue.title,
                    'link': link,
                    'score': score,
                    'summary': issue.body[:200] if issue.body else '',
                    'source': 'GitHub Issues',
                    'keywords': []
                })
    
    if not issues:
        logger.info("今天没有新内容，跳过邮件发送")
        return
    
    issues.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    period = os.getenv("PERIOD", "daily")
    sender.send(issues, period)


if __name__ == "__main__":
    main()

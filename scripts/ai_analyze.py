#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 分析模块
调用 OpenAI API 对内容进行评分、摘要、关键词提取
"""

import os
from loguru import logger
from openai import OpenAI


class AIAnalyzer:
    def __init__(self, config):
        self.config = config
        self.enabled = config['ai']['enabled']
        
        api_key = os.getenv("AI_API_KEY")
        base_url = os.getenv("AI_BASE_URL") or config['ai'].get('base_url', '')
        
        if not api_key:
            logger.warning("AI_API_KEY 未配置，AI 分析将跳过")
            self.enabled = False
            self.client = None
        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url if base_url else None
            )
            logger.info(f"AI 客户端初始化成功，模型：{config['ai']['model']}")
    
    async def analyze(self, item):
        """分析单篇文章"""
        if not self.enabled or not self.client:
            return {
                'score': 70,
                'summary': item.get('summary', '')[:200],
                'keywords': [],
                'one_sentence': ''
            }
        
        try:
            title = item.get('title', '')
            content = item.get('content', '')[:3000]
            
            prompt = f"""请分析以下文章内容，并以 JSON 格式返回结果：

文章标题：{title}

文章内容：{content}

请返回以下字段（必须是合法的 JSON 格式）：
{{
    "score": 0-100 的整数，
    "summary": "200 字以内的中文摘要",
    "keywords": ["关键词 1", "关键词 2", "关键词 3"],
    "one_sentence": "一句话总结（30 字以内）"
}}

评分标准：
- 90-100：顶级技术文章，深度分析，原创内容
- 80-89：优质文章，有实用价值
- 70-79：一般文章，基本信息完整
- 60-69：勉强合格，内容较浅
- 60 以下：低质内容，营销号，广告等

注意：只返回 JSON，不要任何其他文字。"""

            response = self.client.chat.completions.create(
                model=self.config['ai']['model'],
                messages=[
                    {"role": "system", "content": "你是一个专业的内容分析助手，擅长技术文章评估和摘要生成。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=self.config['ai']['max_tokens'],
                timeout=self.config['ai']['timeout']
            )
            
            content_text = response.choices[0].message.content.strip()
            
            # 清理 markdown 标记
            if content_text.startswith('```json'):
                content_text = content_text[7:]
            if content_text.endswith('```'):
                content_text = content_text[:-3]
            content_text = content_text.strip()
            
            import json
            result = json.loads(content_text)
            
            logger.debug(f"AI 分析完成：{title[:30]}... - 评分：{result.get('score')}")
            
            return {
                'score': result.get('score', 70),
                'summary': result.get('summary', ''),
                'keywords': result.get('keywords', []),
                'one_sentence': result.get('one_sentence', ''),
                'ai_analyzed': True
            }
            
        except Exception as e:
            logger.error(f"AI 分析失败：{str(e)}")
            return {
                'score': 70,
                'summary': item.get('summary', '')[:200],
                'keywords': [],
                'one_sentence': '',
                'ai_error': str(e)
            }

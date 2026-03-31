# TrendRadar-Issues

> **BestBlogs 数据** × **TrendRadar 算法** = 智能内容聚合系统
> 
> 使用 BestBlogs 的 400+ 精选 RSS 订阅源（数据），通过 TrendRadar 的热点聚合算法（过滤/去重/评分），输出到 GitHub Issues

## ✨ 核心理念

| 项目 | 核心价值 | 在本项目中的角色 |
|------|---------|---------------|
| **BestBlogs** | 400+ 精选 RSS 订阅源 | **数据源** - 提供优质内容 |
| **TrendRadar** | 热搜聚合算法 | **算法引擎** - 过滤/去重/评分 |

## 🎯 核心功能

### 1. 双数据源聚合

```
┌─────────────────────────────────────────────────────────────┐
│                      数据输入                                │
├──────────────────────────┬──────────────────────────────────┤
│  BestBlogs (RSS)         │  TrendRadar (热搜)               │
│  - 技术文章 170+         │  - 知乎/微博/抖音等 11+ 平台      │
│  - 播客 30+              │  - 实时热点                      │
│  - 视频 40+              │  - 趋势分析                      │
│  - Twitter 160+          │                                  │
│  共计 400+ 精选订阅源     │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

### 2. TrendRadar 算法处理

- ✅ **关键词过滤** - 普通词/必须词/过滤词/全局过滤
- ✅ **去重检测** - 基于标题 + 链接的 MD5 检测
- ✅ **AI 评分** - 0-100 分质量评估
- ✅ **热点权重** - 排名 + 频次 + 热度综合计算

### 3. GitHub Issues 存储

- 每条内容创建一个 Issue
- Label 分类管理
- 自动关闭过期内容

### 4. 邮件汇总推送

- 每日 20:00 发送
- HTML 精美格式

---

## 🚀 快速开始

### 1. Fork 项目

```bash
# 访问 https://github.com/mkafw/TrendRadar-Issues
# 点击右上角 Fork 按钮
```

### 2. 配置 GitHub Secrets

进入 **Settings** → **Secrets and variables** → **Actions**

| Name | 必需 | 示例值 |
|------|------|--------|
| `EMAIL_FROM` | ✅ | `your@gmail.com` |
| `EMAIL_PASSWORD` | ✅ | 邮箱授权码 |
| `EMAIL_TO` | ✅ | `your@gmail.com` |
| `AI_API_KEY` | ✅ | `sk-xxx` |

### 3. 启用 Actions

进入 **Actions** → 点击 **Enable workflows**

### 4. 手动测试

**Actions** → **Fetch and Process** → **Run workflow**

---

## 📁 项目结构

```
TrendRadar-Issues/
├── .github/workflows/
│   ├── fetch.yml          # 主工作流
│   ├── cleanup.yml        # 清理 Issues
│   └── email_summary.yml  # 邮件汇总
│
├── config/
│   ├── config.yaml        # 主配置
│   ├── frequency_words.txt # 关键词（TrendRadar 算法）
│   └── rss_sources.opml   # RSS 订阅源（BestBlogs 数据）
│
├── scripts/
│   ├── main.py            # 主程序
│   ├── fetch_rss.py       # RSS 抓取
│   ├── fetch_hotspots.py  # 热搜抓取
│   ├── ai_analyze.py      # AI 分析
│   ├── create_issues.py   # Issues 管理
│   └── email_summary.py   # 邮件发送
│
└── requirements.txt       # Python 依赖
```

---

## 📊 数据流向

```
┌─────────────────┐    ┌─────────────────┐
│  BestBlogs RSS  │    │  TrendRadar     │
│  (400+ 订阅源)   │    │  热搜 API        │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  TrendRadar 算法      │
         │  - 关键词过滤         │
         │  - 去重检测           │
         │  - AI 评分            │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  GitHub Issues       │
         │  - 自动创建          │
         │  - Label 分类         │
         │  - 定期清理          │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  邮件汇总            │
         │  - 每日 20:00         │
         │  - HTML 格式          │
         └──────────────────────┘
```

---

## ⚙️ 配置说明

### config.yaml

```yaml
# RSS 配置（BestBlogs 数据）
rss:
  enabled: true
  opml_file: "config/rss_sources.opml"  # 400+ 订阅源
  max_articles_per_run: 50

# 热搜配置（TrendRadar 算法）
hotspots:
  enabled: true
  platforms:
    - zhihu
    - weibo
    - douyin
    # ...

# AI 配置
ai:
  enabled: true
  min_score: 60  # 低于 60 分不创建 Issue

# Issues 配置
github:
  auto_create_issues: true
  keep_days: 7  # 7 天后自动关闭
```

### frequency_words.txt

```text
# TrendRadar 关键词过滤算法

# 普通词
AI
大模型
Python

# 必须词
+技术

# 过滤词
!广告
!培训

# 全局过滤
[GLOBAL_FILTER]
震惊
标题党
```

---

## 🏷️ Issue Label

| Label | 说明 | 颜色 |
|-------|------|------|
| `rss-article` | RSS 文章 | #1D76DB |
| `hotspot` | 平台热搜 | #D93F0B |
| `ai-score-90+` | 90 分以上 | #0E8A16 |
| `ai-score-80+` | 80-89 分 | #53B358 |
| `ai-score-70+` | 70-79 分 | #AED581 |
| `featured` | 精选（85+） | #FFD700 |

---

## 📝 更新日志

### v1.0.0 (2026-03-31)

- ✅ 整合 BestBlogs 400+ RSS 订阅源
- ✅ 整合 TrendRadar 热搜聚合算法
- ✅ GitHub Issues 存储
- ✅ AI 智能分析
- ✅ 邮件汇总推送

---

## 🙏 致谢

- **数据源**: [BestBlogs](https://github.com/ginobefun/BestBlogs) - 400+ 精选 RSS 订阅源
- **算法引擎**: [TrendRadar](https://github.com/mkafw/TrendRadar) - 热点聚合算法（作者：mkafw）

---

## 📄 License

GPL-3.0 License

# 🚀 TrendRadar-Issues 快速部署指南

## 5 分钟部署完成

### 步骤 1: Fork 项目（1 分钟）

```bash
# 访问 https://github.com/mkafw/TrendRadar-Issues
# 点击右上角 Fork 按钮
```

### 步骤 2: 配置 Secrets（3 分钟）

进入 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

#### 必需配置（4 个）

| Name | 示例值 | 说明 |
|------|--------|------|
| `EMAIL_FROM` | `your@gmail.com` | 发件人邮箱 |
| `EMAIL_PASSWORD` | `abcdefghijklmnop` | 邮箱授权码（非登录密码！） |
| `EMAIL_TO` | `your@gmail.com` | 收件人邮箱 |
| `AI_API_KEY` | `sk-xxx` | OpenAI/DeepSeek API Key |

**邮箱授权码获取**：
- Gmail：Google 账户 → 安全性 → 应用专用密码
- QQ 邮箱：设置 → 账户 → 开启 POP3/SMTP → 获取授权码
- 163 邮箱：设置 → POP3/SMTP/IMAP → 开启 SMTP → 获取授权码

### 步骤 3: 启用 Actions（1 分钟）

```bash
# 进入 Actions 标签页
# 点击 "Enable workflows"
```

### 步骤 4: 手动测试（5 分钟）

```bash
# Actions → Fetch and Process → Run workflow
# Source type 选择 both
# 点击 Run workflow
# 等待 3-5 分钟
```

### 步骤 5: 验证结果

- ✅ **Issues** 标签页有新 Issue
- ✅ **邮箱** 收到汇总邮件（如果有内容）

---

## 📊 运行时间（北京时间）

| 任务 | 时间 | 频率 |
|------|------|------|
| RSS 抓取 | 每 2 小时 | 12 次/天 |
| 热搜抓取 | 每小时 30 分 | 24 次/天 |
| Issues 清理 | 每天 10:00 | 1 次/天 |
| 邮件汇总 | 每天 20:00 | 1 次/天 |

---

## 🔧 自定义配置

### 修改关键词

编辑 `config/frequency_words.txt`：

```text
# 添加你关心的关键词
AI
大模型
Python
GitHub

# 排除不想要的
!广告
!培训
!营销号
```

### 修改 AI 评分阈值

编辑 `config/config.yaml`：

```yaml
ai:
  min_score: 60  # 低于 60 分不创建 Issue
```

### 修改 Issue 保留天数

编辑 `config/config.yaml`：

```yaml
filter:
  keep_days: 7  # 7 天后自动关闭
```

---

## 📝 完整文档

- [README.md](README.md) - 完整功能说明
- [DEPLOY.md](DEPLOY.md) - 详细部署指南
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构

---

## 💡 提示

- ⚠️ GitHub Actions 使用 UTC 时间，北京时间 = UTC + 8
- ⚠️ 邮箱授权码 ≠ 登录密码
- ⚠️ AI 分析可选，不配置也能运行（使用默认评分）

**祝使用愉快！** 🎉

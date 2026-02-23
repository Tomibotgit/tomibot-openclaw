# Hyvor Relay Email Skill

一个完整的 Hyvor Relay 自托管邮箱服务 Skill，提供发送邮件、接收邮件、附件处理等功能。

## 🚀 快速开始

### 安装

```bash
# 1. 安装 Skill
npx skillsadd tomibot/hyvor-relay-email

# 2. 安装 Hyvor Relay 服务
./scripts/install.sh

# 3. 配置客户端
python scripts/configure.py
```

### 基本使用

```python
from hyvor_relay.client import HyvorRelayClient

# 初始化客户端（自动读取环境变量）
client = HyvorRelayClient()

# 发送简单邮件
response = client.send_email_simple(
    to="recipient@example.com",
    subject="测试邮件",
    body="这是一封测试邮件"
)

print(f"邮件发送成功！ID: {response['id']}")
```

## 📦 功能特性

✅ **发送邮件** - 支持 HTML/纯文本、附件、自定义头部  
✅ **接收邮件** - 通过 Webhook 接收邮件通知  
✅ **附件处理** - 支持 Base64 编码的附件  
✅ **自定义域名** - 支持绑定自己的邮箱域名  
✅ **队列管理** - 事务性和分发性邮件队列分离  
✅ **邮件日志** - 30天邮件发送日志和 SMTP 对话记录  
✅ **Webhook 集成** - 实时邮件事件通知  
✅ **多租户支持** - 支持多个项目和租户  

## 🛠️ 安装方法

### Docker Compose（推荐）

```bash
# 克隆仓库
git clone https://github.com/hyvor/relay.git
cd relay

# 启动服务
docker-compose up -d
```

### 脚本安装

```bash
# 使用安装脚本
./scripts/install.sh /opt/hyvor-relay

# 带测试的安装
./scripts/install.sh --test

# 交互式配置
./scripts/install.sh --configure
```

## ⚙️ 配置

### 环境变量

```bash
# 必需配置
export HYVOR_RELAY_URL=http://localhost:8080
export HYVOR_RELAY_API_KEY=your_api_key_here

# 可选配置
export HYVOR_RELAY_PROJECT_ID=default
export HYVOR_RELAY_FROM_EMAIL=noreply@yourdomain.com
```

### 配置文件

```json
{
  "base_url": "http://localhost:8080",
  "api_key": "your_api_key",
  "project_id": "default",
  "default_from_email": "noreply@yourdomain.com"
}
```

## 📝 使用示例

### 发送邮件

```python
from hyvor_relay.client import HyvorRelayClient, Attachment

# 初始化客户端
client = HyvorRelayClient()

# 发送简单邮件
response = client.send_email_simple(
    to="user@example.com",
    subject="欢迎邮件",
    body="欢迎使用我们的服务！"
)

# 发送 HTML 邮件
response = client.send_email(
    to="user@example.com",
    subject="HTML 邮件",
    body_html="<h1>欢迎</h1><p>这是一封 HTML 邮件</p>",
    body_text="欢迎使用我们的服务！"
)

# 发送带附件的邮件
attachment = client.create_attachment_from_file("document.pdf")
response = client.send_email(
    to="user@example.com",
    subject="带附件的邮件",
    body_text="请查看附件",
    attachments=[attachment]
)

# 发送给多个收件人
response = client.send_email(
    to=["user1@example.com", "user2@example.com"],
    cc="manager@example.com",
    subject="团队通知",
    body_text="这是团队通知邮件"
)
```

### Webhook 接收邮件

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/email', methods=['POST'])
def email_webhook():
    data = request.json
    event_type = data.get('event')
    
    if event_type == 'email.delivered':
        # 处理邮件送达
        print(f"邮件已送达: {data.get('email_id')}")
    elif event_type == 'email.bounced':
        # 处理邮件退回
        print(f"邮件退回: {data.get('email_id')}")
    
    return jsonify({"status": "ok"})
```

## 🔧 工具脚本

### 配置脚本

```bash
# 交互式配置
python scripts/configure.py

# 快速配置
python scripts/configure.py --quick

# 测试连接
python scripts/configure.py --test

# 发送测试邮件
python scripts/configure.py --send-test
```

### 测试脚本

```bash
# 测试所有功能
python scripts/test_email.py --to test@example.com

# 测试 HTML 邮件
python scripts/test_email.py --to test@example.com --test html

# 测试带附件
python scripts/test_email.py --to test@example.com --attach file1.pdf file2.jpg

# 测试多个收件人
python scripts/test_email.py --to test@example.com --recipients user1@example.com user2@example.com
```

### 监控脚本

```bash
# 实时监控
python scripts/monitor.py --interval 60

# 保存监控数据
python scripts/monitor.py --output /var/log/hyvor-metrics.json

# 生成报告
python scripts/monitor.py --report 24

# 单次运行
python scripts/monitor.py --once
```

## 🏗️ 集成示例

### Flask 集成

```python
from flask import Flask, request, jsonify
from hyvor_relay.client import HyvorRelayClient

app = Flask(__name__)
client = HyvorRelayClient()

@app.route('/send-newsletter', methods=['POST'])
def send_newsletter():
    data = request.json
    response = client.send_email(
        to=data['recipients'],
        subject=data['subject'],
        body_html=data['content']
    )
    return jsonify({"message_id": response['id']})
```

### Django 集成

```python
# settings.py
HYVOR_RELAY = {
    'BASE_URL': 'http://localhost:8080',
    'API_KEY': 'your_api_key',
    'DEFAULT_FROM_EMAIL': 'noreply@yourdomain.com'
}

# utils/email.py
from django.conf import settings
from hyvor_relay.client import HyvorRelayClient

def send_django_email(subject, message, recipient_list, html_message=None):
    client = HyvorRelayClient(
        base_url=settings.HYVOR_RELAY['BASE_URL'],
        api_key=settings.HYVOR_RELAY['API_KEY']
    )
    
    return client.send_email(
        to=recipient_list,
        subject=subject,
        body_html=html_message or message,
        body_text=message,
        from_email=settings.HYVOR_RELAY['DEFAULT_FROM_EMAIL']
    )
```

### FastAPI 集成

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from hyvor_relay.client import HyvorRelayClient

app = FastAPI()
client = HyvorRelayClient()

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    html: bool = False

@app.post("/send-email")
async def send_email(request: EmailRequest):
    try:
        if request.html:
            response = client.send_email(
                to=request.to,
                subject=request.subject,
                body_html=request.body
            )
        else:
            response = client.send_email(
                to=request.to,
                subject=request.subject,
                body_text=request.body
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📊 API 参考

### 发送邮件

```
POST /api/console/sends
```

**请求体：**
```json
{
  "from": {
    "name": "发件人名称",
    "email": "noreply@yourdomain.com"
  },
  "to": "recipient@example.com",
  "subject": "邮件主题",
  "body_html": "<h1>HTML 内容</h1>",
  "body_text": "纯文本内容",
  "attachments": [
    {
      "content": "base64编码的内容",
      "name": "filename.pdf",
      "content_type": "application/pdf"
    }
  ]
}
```

### Webhook 事件

- `email.sent` - 邮件已发送
- `email.delivered` - 邮件已送达
- `email.bounced` - 邮件退回
- `email.complained` - 用户投诉
- `domain.verified` - 域名已验证
- `suppression.added` - 添加到抑制列表

## 🔍 故障排除

### 常见问题

1. **API 密钥无效**
   - 检查密钥是否具有 `sends.send` 权限
   - 确认密钥是否属于正确的项目

2. **域名验证失败**
   - 检查 DNS 记录是否正确
   - 等待 DNS 传播（最多 48 小时）

3. **附件大小限制**
   - 默认限制：10MB
   - 可在配置中调整

4. **发送频率限制**
   - 默认：10 请求/秒，100 请求/分钟
   - 查看响应头中的速率限制信息

### 日志查看

```bash
# 查看 Docker 日志
docker-compose logs -f relay

# 查看特定服务日志
docker-compose logs -f relay-api
docker-compose logs -f relay-worker
```

## 📈 性能优化

### 批量发送

```python
import asyncio

# 使用异步发送提高性能
async def send_batch_emails(emails):
    tasks = []
    for email in emails:
        task = asyncio.create_task(
            client.send_email_async(**email)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 连接池

```python
# 配置连接池
client = HyvorRelayClient(
    base_url="http://localhost:8080",
    api_key="your_api_key",
    pool_connections=10,
    pool_maxsize=10,
    max_retries=3
)
```

## 🔒 安全建议

1. **API 密钥安全**
   - 不要将密钥提交到版本控制
   - 使用环境变量或密钥管理服务
   - 定期轮换密钥

2. **HTTPS 配置**
   - 生产环境必须使用 HTTPS
   - 配置有效的 SSL 证书
   - 启用 HSTS

3. **访问控制**
   - 限制 API 访问 IP
   - 使用防火墙规则
   - 监控异常访问

## 📄 许可证

Hyvor Relay 使用 AGPL-3.0 许可证。对于商业用途，可以考虑购买企业许可证。

## 🤝 支持与贡献

- 官方文档：https://relay.hyvor.com/docs
- GitHub 仓库：https://github.com/hyvor/relay
- 社区支持：https://hyvor.community
- Discord：https://hyvor.com/go/discord

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱：tomibot@163.com
- GitHub Issues：https://github.com/tomibot/hyvor-relay-email/issues

---

**注意**: 本 Skill 需要先部署 Hyvor Relay 实例才能使用。请参考安装部分进行部署。
# Hyvor Relay Email Skill

一个完整的 Hyvor Relay 自托管邮箱服务 Skill，提供发送邮件、接收邮件、附件处理等功能。

## 概述

Hyvor Relay 是一个开源的、可自托管的邮件 API，专为开发者设计。它是 SES、Mailgun、SendGrid 的自托管替代方案。

## 功能特性

✅ **发送邮件** - 支持 HTML/纯文本、附件、自定义头部
✅ **接收邮件** - 通过 Webhook 接收邮件通知
✅ **附件处理** - 支持 Base64 编码的附件
✅ **自定义域名** - 支持绑定自己的邮箱域名
✅ **队列管理** - 事务性和分发性邮件队列分离
✅ **邮件日志** - 30天邮件发送日志和 SMTP 对话记录
✅ **Webhook 集成** - 实时邮件事件通知
✅ **多租户支持** - 支持多个项目和租户

## 安装方法

### 方法1：Docker Compose（推荐）

```bash
# 克隆仓库
git clone https://github.com/hyvor/relay.git
cd relay

# 启动服务
docker-compose up -d
```

### 方法2：Docker Swarm

```bash
# 部署到 Swarm
docker stack deploy -c docker-compose.yml relay
```

### 方法3：手动安装

参考官方文档：https://relay.hyvor.com/hosting

## 配置说明

### 环境变量

```bash
# 必需配置
HYVOR_RELAY_URL=http://localhost:8080  # Hyvor Relay 实例地址
HYVOR_RELAY_API_KEY=your_api_key_here  # API 密钥

# 可选配置
HYVOR_RELAY_PROJECT_ID=default         # 项目ID（默认为"default"）
HYVOR_RELAY_DOMAIN=yourdomain.com      # 默认发送域名
HYVOR_RELAY_FROM_EMAIL=noreply@yourdomain.com  # 默认发件人
```

### API 密钥获取

1. 访问 Hyvor Relay 控制台（通常是 `http://localhost:8080/console`）
2. 登录并创建项目
3. 进入项目 → API Keys → 创建新密钥
4. 确保勾选 `sends.send` 权限

## 使用方法

### 发送邮件

```python
from hyvor_relay import HyvorRelayClient

# 初始化客户端
client = HyvorRelayClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)

# 发送简单邮件
response = client.send_email(
    to="recipient@example.com",
    subject="测试邮件",
    body_text="这是一封测试邮件",
    from_email="noreply@yourdomain.com"
)

# 发送带附件的邮件
with open("document.pdf", "rb") as f:
    attachment_content = f.read()

response = client.send_email(
    to=["user1@example.com", "user2@example.com"],
    cc="cc@example.com",
    bcc=["bcc1@example.com", "bcc2@example.com"],
    subject="带附件的邮件",
    body_html="<h1>HTML 内容</h1><p>这是一封带附件的邮件</p>",
    body_text="纯文本内容",
    attachments=[
        {
            "name": "document.pdf",
            "content": attachment_content,  # bytes 或 base64 字符串
            "content_type": "application/pdf"
        }
    ]
)
```

### 接收邮件（通过 Webhook）

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/email', methods=['POST'])
def email_webhook():
    """处理邮件事件 Webhook"""
    data = request.json
    
    event_type = data.get('event')
    
    if event_type == 'email.delivered':
        # 邮件已送达
        email_id = data.get('email_id')
        recipient = data.get('recipient')
        print(f"邮件已送达: {email_id} -> {recipient}")
        
    elif event_type == 'email.bounced':
        # 邮件退回
        email_id = data.get('email_id')
        bounce_type = data.get('bounce_type')
        print(f"邮件退回: {email_id} - {bounce_type}")
        
    elif event_type == 'email.complained':
        # 用户投诉
        email_id = data.get('email_id')
        print(f"用户投诉: {email_id}")
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=5000)
```

### 查询邮件状态

```python
# 查询邮件发送状态
status = client.get_email_status(email_id="email_123")

# 获取发送日志
logs = client.get_send_logs(
    start_date="2024-01-01",
    end_date="2024-01-31",
    limit=100
)
```

## API 参考

### 发送邮件端点

```
POST /api/console/sends
```

**请求体示例：**
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

### Webhook 事件类型

- `email.sent` - 邮件已发送
- `email.delivered` - 邮件已送达
- `email.bounced` - 邮件退回
- `email.complained` - 用户投诉
- `domain.verified` - 域名已验证
- `suppression.added` - 添加到抑制列表

## 工具脚本

本 Skill 包含以下实用脚本：

### 1. 安装脚本 (`scripts/install.sh`)
```bash
# 安装 Hyvor Relay
./scripts/install.sh

# 指定安装路径
./scripts/install.sh /opt/hyvor-relay
```

### 2. 配置脚本 (`scripts/configure.py`)
```python
# 交互式配置
python scripts/configure.py

# 命令行配置
python scripts/configure.py --url http://localhost:8080 --api-key YOUR_KEY
```

### 3. 测试脚本 (`scripts/test_email.py`)
```python
# 测试邮件发送
python scripts/test_email.py --to test@example.com

# 测试带附件
python scripts/test_email.py --to test@example.com --attach file.pdf
```

### 4. 监控脚本 (`scripts/monitor.py`)
```python
# 监控邮件队列
python scripts/monitor.py --interval 60

# 监控特定项目
python scripts/monitor.py --project-id myproject
```

## 集成示例

### 与 Flask 集成
```python
from flask import Flask, request
from hyvor_relay import HyvorRelayClient

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
    return {"message_id": response['id']}
```

### 与 Django 集成
```python
# settings.py
HYVOR_RELAY = {
    'BASE_URL': 'http://localhost:8080',
    'API_KEY': 'your_api_key',
    'DEFAULT_FROM_EMAIL': 'noreply@yourdomain.com'
}

# utils/email.py
from django.conf import settings
from hyvor_relay import HyvorRelayClient

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

### 与 FastAPI 集成
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from hyvor_relay import HyvorRelayClient

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

## 故障排除

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

## 性能优化

### 批量发送
```python
# 使用批量发送提高性能
emails = [
    {"to": "user1@example.com", "subject": "邮件1", "body": "内容1"},
    {"to": "user2@example.com", "subject": "邮件2", "body": "内容2"},
]

for email in emails:
    # 使用异步发送
    asyncio.create_task(client.send_email_async(**email))
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

## 安全建议

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

## 扩展开发

### 自定义中间件
```python
class LoggingMiddleware:
    def __init__(self, client):
        self.client = client
    
    def send_email(self, **kwargs):
        print(f"发送邮件到: {kwargs.get('to')}")
        start_time = time.time()
        response = self.client.send_email(**kwargs)
        elapsed = time.time() - start_time
        print(f"邮件发送完成，耗时: {elapsed:.2f}秒")
        return response

# 使用中间件
client = HyvorRelayClient()
logging_client = LoggingMiddleware(client)
```

### 插件系统
```python
# 创建插件
class AttachmentValidatorPlugin:
    def pre_send(self, email_data):
        # 验证附件
        for attachment in email_data.get('attachments', []):
            if attachment['size'] > 10 * 1024 * 1024:  # 10MB
                raise ValueError("附件大小超过限制")
        return email_data
    
    def post_send(self, response):
        # 记录发送结果
        log_to_database(response)
        return response

# 注册插件
client.register_plugin(AttachmentValidatorPlugin())
```

## 许可证

Hyvor Relay 使用 AGPL-3.0 许可证。对于商业用途，可以考虑购买企业许可证。

## 支持与贡献

- 官方文档：https://relay.hyvor.com/docs
- GitHub 仓库：https://github.com/hyvor/relay
- 社区支持：https://hyvor.community
- Discord：https://hyvor.com/go/discord

## 更新日志

### v1.0.0 (2026-02-24)
- 初始版本发布
- 支持邮件发送和接收
- 包含完整的 Python 客户端
- 提供多种框架集成示例

---

**注意**: 本 Skill 需要先部署 Hyvor Relay 实例才能使用。请参考安装部分进行部署。
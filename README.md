# TomiBot OpenClaw Workspace

这是一个 OpenClaw AI 助手的工作空间，包含智能体配置、技能和项目文件。

## 项目结构

```
tomibot-openclaw/
├── AGENTS.md          # 智能体工作空间指南
├── SOUL.md           # 智能体身份定义
├── USER.md           # 用户信息
├── IDENTITY.md       # 智能体身份
├── TOOLS.md          # 工具配置
├── HEARTBEAT.md      # 心跳任务
├── memory/           # 记忆文件
│   └── 2026-02-24.md # 今日记忆
├── skills/           # 技能目录
│   └── hyvor-relay-email/  # Hyvor Relay 邮件服务技能
└── agents/           # 智能体配置
    ├── designer/     # 设计狮智能体
    ├── researcher/   # 情报猿智能体
    ├── coder/        # 程序猿智能体
    ├── trainer/      # 训练狮智能体
    └── media_ops/    # 自媒体运营狮智能体
```

## 智能体阵容

1. **🤖 TomiBot (main)** - 主助手
2. **🦁 训练狮 (trainer)** - 训练专家
3. **📱 自媒体运营狮 (media_ops)** - 内容运营专家
4. **🦁 设计狮 (designer)** - 视觉设计专家
5. **🐵 情报猿 (researcher)** - 商业情报专家
6. **🐒 程序猿 (coder)** - 全栈开发专家 (DeepSeek-R1)

## 核心功能

### 智能体系统
- 6个专业智能体，各司其职
- 支持智能路由 (`sessions_spawn`)
- 每个智能体有独立的身份和专长

### 技能系统
- **Hyvor Relay Email Skill**: 完整的自托管邮件服务
- 支持邮件发送、接收、附件处理
- 提供多种框架集成示例

### 配置管理
- 智能体 allowlist 配置
- 模型配置 (DeepSeek-R1 等)
- 工作空间管理

## 使用说明

### 启动智能体
```bash
# 启动主智能体
openclaw start

# 调用专业智能体
sessions_spawn agentId=coder task="创建一个简单的HTTP服务器"
```

### 邮件服务
```python
# 使用 Hyvor Relay 发送邮件
from hyvor_relay import HyvorRelayClient

client = HyvorRelayClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)

client.send_email(
    to="recipient@example.com",
    subject="测试邮件",
    body_text="这是一封测试邮件"
)
```

## 开发状态

### ✅ 已完成
- [x] 6个专业智能体配置完成
- [x] 智能体 allowlist 配置
- [x] Hyvor Relay Email Skill 创建
- [x] 工作空间基础配置

### 🔄 进行中
- [ ] GitHub 项目同步
- [ ] 邮件服务部署
- [ ] 智能体技能扩展

### 📋 计划中
- [ ] 智能体协作工作流
- [ ] 更多专业技能开发
- [ ] 生产环境部署

## 技术栈

- **AI 模型**: DeepSeek-R1, DeepSeek-V3, Kimi
- **框架**: OpenClaw AI 助手平台
- **邮件服务**: Hyvor Relay (自托管)
- **版本控制**: Git + GitHub
- **部署**: Docker (计划中)

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系

- 项目维护: TomiBot
- 创建时间: 2026年2月24日
- 最后更新: 2026年2月24日
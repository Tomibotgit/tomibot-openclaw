#!/usr/bin/env python3
"""
Hyvor Relay 测试脚本
测试邮件发送功能
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from hyvor_relay.client import HyvorRelayClient, Attachment, EmailAddress


def load_config(config_path: Optional[Path] = None) -> dict:
    """加载配置"""
    if config_path and config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 从环境变量加载
    config = {
        "base_url": os.getenv("HYVOR_RELAY_URL", "http://localhost:8080"),
        "api_key": os.getenv("HYVOR_RELAY_API_KEY"),
        "project_id": os.getenv("HYVOR_RELAY_PROJECT_ID", "default"),
        "default_from_email": os.getenv("HYVOR_RELAY_FROM_EMAIL", "noreply@localhost")
    }
    
    return config


def test_simple_email(client: HyvorRelayClient, to_email: str, from_email: str) -> bool:
    """测试简单邮件"""
    print("📧 测试简单邮件...")
    
    try:
        response = client.send_email_simple(
            to=to_email,
            subject="Hyvor Relay 简单测试邮件",
            body="这是一封简单的测试邮件。\n\n如果收到此邮件，说明简单邮件发送功能正常。",
            from_email=from_email
        )
        
        print(f"✅ 简单邮件发送成功！")
        print(f"   邮件ID: {response.get('id', 'N/A')}")
        print(f"   状态: {response.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 简单邮件发送失败: {e}")
        return False


def test_html_email(client: HyvorRelayClient, to_email: str, from_email: str) -> bool:
    """测试 HTML 邮件"""
    print("🎨 测试 HTML 邮件...")
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试邮件</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px;
        }
        .content {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Hyvor Relay 测试邮件</h1>
    </div>
    
    <div class="content">
        <h2>HTML 邮件测试</h2>
        <p>这是一封 <strong>HTML 格式</strong> 的测试邮件。</p>
        
        <h3>功能测试：</h3>
        <ul>
            <li>✅ HTML 渲染</li>
            <li>✅ CSS 样式</li>
            <li>✅ 响应式设计</li>
            <li>✅ 特殊字符和表情</li>
        </ul>
        
        <p>如果看到此邮件，说明 HTML 邮件功能正常。</p>
        
        <blockquote style="border-left: 4px solid #4CAF50; padding-left: 15px; margin: 20px 0;">
            <p><em>"好的设计是显而易见的，伟大的设计是透明的。"</em></p>
        </blockquote>
    </div>
    
    <div class="footer">
        <p>此邮件由 Hyvor Relay 发送</p>
        <p>发送时间: <!--DATE--></p>
    </div>
</body>
</html>
"""
    
    try:
        response = client.send_email(
            to=to_email,
            subject="Hyvor Relay HTML 测试邮件",
            body_html=html_content,
            body_text="这是一封 HTML 测试邮件。请使用支持 HTML 的邮件客户端查看。",
            from_email=from_email
        )
        
        print(f"✅ HTML 邮件发送成功！")
        print(f"   邮件ID: {response.get('id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML 邮件发送失败: {e}")
        return False


def test_attachment_email(client: HyvorRelayClient, to_email: str, from_email: str, 
                         attachment_paths: List[str]) -> bool:
    """测试带附件的邮件"""
    print("📎 测试带附件的邮件...")
    
    attachments = []
    
    for path in attachment_paths:
        if os.path.exists(path):
            try:
                attachment = client.create_attachment_from_file(path)
                attachments.append(attachment)
                print(f"   添加附件: {path}")
            except Exception as e:
                print(f"   ⚠️  添加附件失败 {path}: {e}")
        else:
            print(f"   ⚠️  文件不存在: {path}")
    
    if not attachments:
        print("   ⚠️  没有有效的附件，跳过附件测试")
        return False
    
    try:
        response = client.send_email(
            to=to_email,
            subject="Hyvor Relay 带附件测试邮件",
            body_text=f"这是一封带附件的测试邮件。\n\n共包含 {len(attachments)} 个附件。",
            from_email=from_email,
            attachments=attachments
        )
        
        print(f"✅ 带附件邮件发送成功！")
        print(f"   邮件ID: {response.get('id', 'N/A')}")
        print(f"   附件数量: {len(attachments)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 带附件邮件发送失败: {e}")
        return False


def test_multiple_recipients(client: HyvorRelayClient, recipients: List[str], from_email: str) -> bool:
    """测试多个收件人"""
    print("👥 测试多个收件人...")
    
    if len(recipients) < 2:
        print("   ⚠️  需要至少2个收件人进行测试")
        return False
    
    try:
        response = client.send_email(
            to=recipients,
            subject="Hyvor Relay 多收件人测试邮件",
            body_text="这是一封发送给多个收件人的测试邮件。\n\n每个收件人都应该收到此邮件。",
            from_email=from_email,
            cc=[recipients[0]] if len(recipients) > 1 else None,
            bcc=[recipients[1]] if len(recipients) > 2 else None
        )
        
        print(f"✅ 多收件人邮件发送成功！")
        print(f"   邮件ID: {response.get('id', 'N/A')}")
        print(f"   收件人数量: {len(recipients)}")
        print(f"   收件人: {', '.join(recipients[:3])}{'...' if len(recipients) > 3 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ 多收件人邮件发送失败: {e}")
        return False


def test_connection(client: HyvorRelayClient) -> bool:
    """测试连接"""
    print("🔧 测试连接...")
    
    try:
        if client.test_connection():
            print("✅ 连接成功！")
            
            # 获取速率限制信息
            rate_info = client.get_rate_limit_info()
            if rate_info:
                print("📊 速率限制信息:")
                for key, value in rate_info.items():
                    print(f"   {key}: {value}")
            
            return True
        else:
            print("❌ 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Hyvor Relay 测试脚本")
    parser.add_argument("--to", "-t", required=True,
                       help="收件人邮箱地址")
    parser.add_argument("--from", "-f", dest="from_email",
                       help="发件人邮箱地址")
    parser.add_argument("--config", "-c", default="~/.hyvor-relay/config.json",
                       help="配置文件路径")
    parser.add_argument("--attach", "-a", nargs="+",
                       help="附件文件路径")
    parser.add_argument("--recipients", "-r", nargs="+",
                       help="多个收件人邮箱地址")
    parser.add_argument("--test", choices=["all", "simple", "html", "attachment", "multi", "connection"],
                       default="all", help="测试类型")
    
    args = parser.parse_args()
    
    # 加载配置
    config_path = Path(args.config).expanduser()
    config = load_config(config_path)
    
    # 设置发件人
    from_email = args.from_email or config.get("default_from_email", "noreply@localhost")
    
    # 创建客户端
    try:
        client = HyvorRelayClient(
            base_url=config.get("base_url"),
            api_key=config.get("api_key"),
            project_id=config.get("project_id", "default")
        )
    except Exception as e:
        print(f"❌ 创建客户端失败: {e}")
        print("请检查配置文件和 API Key")
        sys.exit(1)
    
    print("🚀 Hyvor Relay 测试开始")
    print("=" * 50)
    print(f"服务地址: {config.get('base_url')}")
    print(f"发件人: {from_email}")
    print(f"收件人: {args.to}")
    print("")
    
    test_results = {}
    
    # 根据测试类型执行测试
    if args.test in ["all", "connection"]:
        test_results["connection"] = test_connection(client)
    
    if args.test in ["all", "simple"]:
        test_results["simple"] = test_simple_email(client, args.to, from_email)
    
    if args.test in ["all", "html"]:
        test_results["html"] = test_html_email(client, args.to, from_email)
    
    if args.test in ["all", "attachment"] and args.attach:
        test_results["attachment"] = test_attachment_email(client, args.to, from_email, args.attach)
    
    if args.test in ["all", "multi"] and args.recipients:
        test_results["multi"] = test_multiple_recipients(client, args.recipients, from_email)
    
    # 显示测试结果
    print("\n📊 测试结果汇总")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15} {status}")
    
    print("-" * 50)
    print(f"总计: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Hyvor Relay 配置脚本
交互式配置 Hyvor Relay 客户端
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from hyvor_relay.client import HyvorRelayClient, HyvorRelayError


def get_input(prompt: str, default: str = "") -> str:
    """获取用户输入"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value if value else default


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """获取是/否输入"""
    choices = "Y/n" if default else "y/N"
    prompt = f"{prompt} [{choices}]: "
    
    while True:
        value = input(prompt).strip().lower()
        
        if not value:
            return default
        elif value in ["y", "yes"]:
            return True
        elif value in ["n", "no"]:
            return False
        else:
            print("请输入 y/n 或直接回车使用默认值")


def save_config(config: Dict[str, Any], config_path: Path) -> None:
    """保存配置到文件"""
    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存为 JSON
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置已保存到: {config_path}")
    
    # 保存为环境变量文件
    env_path = config_path.parent / ".env"
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# Hyvor Relay 环境变量\n")
        for key, value in config.items():
            if value:  # 只保存非空值
                f.write(f"{key.upper()}={value}\n")
    
    print(f"✅ 环境变量文件: {env_path}")


def test_connection(config: Dict[str, Any]) -> bool:
    """测试连接"""
    print("\n🔧 测试连接...")
    
    try:
        client = HyvorRelayClient(
            base_url=config.get("base_url"),
            api_key=config.get("api_key"),
            project_id=config.get("project_id", "default")
        )
        
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


def send_test_email(config: Dict[str, Any]) -> bool:
    """发送测试邮件"""
    print("\n📧 发送测试邮件...")
    
    to_email = get_input("请输入测试邮箱地址", "test@example.com")
    
    if not to_email or "@" not in to_email:
        print("❌ 邮箱地址无效")
        return False
    
    try:
        client = HyvorRelayClient(
            base_url=config.get("base_url"),
            api_key=config.get("api_key"),
            project_id=config.get("project_id", "default")
        )
        
        response = client.send_email_simple(
            to=to_email,
            subject="Hyvor Relay 测试邮件",
            body="这是一封来自 Hyvor Relay 的测试邮件。\n\n如果收到此邮件，说明配置成功！",
            from_email=config.get("default_from_email")
        )
        
        print(f"✅ 测试邮件已发送！")
        print(f"   邮件ID: {response.get('id', 'N/A')}")
        print(f"   状态: {response.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 发送测试邮件失败: {e}")
        return False


def interactive_config() -> Dict[str, Any]:
    """交互式配置"""
    print("🎯 Hyvor Relay 配置向导")
    print("=" * 50)
    
    config = {}
    
    # 基本配置
    print("\n📋 基本配置")
    print("-" * 30)
    
    config["base_url"] = get_input(
        "Hyvor Relay 服务地址",
        os.getenv("HYVOR_RELAY_URL", "http://localhost:8080")
    )
    
    config["api_key"] = get_input(
        "API Key",
        os.getenv("HYVOR_RELAY_API_KEY", "")
    )
    
    config["project_id"] = get_input(
        "项目ID",
        os.getenv("HYVOR_RELAY_PROJECT_ID", "default")
    )
    
    config["default_from_email"] = get_input(
        "默认发件人邮箱",
        os.getenv("HYVOR_RELAY_FROM_EMAIL", "noreply@localhost")
    )
    
    # 高级配置
    print("\n⚙️  高级配置")
    print("-" * 30)
    
    if get_yes_no("是否配置高级选项", False):
        config["timeout"] = int(get_input("请求超时时间（秒）", "30"))
        config["max_retries"] = int(get_input("最大重试次数", "3"))
        config["pool_connections"] = int(get_input("连接池大小", "10"))
        config["pool_maxsize"] = int(get_input("最大连接数", "10"))
    
    return config


def load_existing_config(config_path: Path) -> Dict[str, Any]:
    """加载现有配置"""
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载现有配置失败: {e}")
    
    return {}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Hyvor Relay 配置脚本")
    parser.add_argument("--config", "-c", default="~/.hyvor-relay/config.json",
                       help="配置文件路径")
    parser.add_argument("--test", "-t", action="store_true",
                       help="测试连接")
    parser.add_argument("--send-test", "-s", action="store_true",
                       help="发送测试邮件")
    parser.add_argument("--show", action="store_true",
                       help="显示当前配置")
    parser.add_argument("--quick", "-q", action="store_true",
                       help="快速配置（使用默认值）")
    
    args = parser.parse_args()
    
    # 解析配置文件路径
    config_path = Path(args.config).expanduser()
    
    # 显示配置
    if args.show:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            print("📄 当前配置:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print("❌ 配置文件不存在")
        return
    
    # 加载或创建配置
    if config_path.exists() and not args.quick:
        config = load_existing_config(config_path)
        print(f"📁 加载现有配置: {config_path}")
        
        if not get_yes_no("是否使用现有配置", True):
            config = interactive_config()
    else:
        if args.quick:
            # 快速配置
            config = {
                "base_url": os.getenv("HYVOR_RELAY_URL", "http://localhost:8080"),
                "api_key": os.getenv("HYVOR_RELAY_API_KEY", ""),
                "project_id": os.getenv("HYVOR_RELAY_PROJECT_ID", "default"),
                "default_from_email": os.getenv("HYVOR_RELAY_FROM_EMAIL", "noreply@localhost")
            }
            print("⚡ 使用快速配置")
        else:
            config = interactive_config()
    
    # 保存配置
    save_config(config, config_path)
    
    # 测试连接
    if args.test or get_yes_no("是否测试连接", True):
        if not config.get("api_key"):
            print("⚠️  未设置 API Key，跳过连接测试")
            print("   请先获取 API Key: https://relay.hyvor.com/console")
        else:
            test_connection(config)
    
    # 发送测试邮件
    if args.send_test or get_yes_no("是否发送测试邮件", False):
        if not config.get("api_key"):
            print("⚠️  未设置 API Key，跳过测试邮件")
        else:
            send_test_email(config)
    
    # 使用说明
    print("\n📚 使用说明:")
    print("=" * 50)
    
    print("\n1. Python 代码中使用:")
    print("""
from hyvor_relay.client import HyvorRelayClient

# 从配置文件加载
import json
with open('~/.hyvor-relay/config.json') as f:
    config = json.load(f)

client = HyvorRelayClient(
    base_url=config['base_url'],
    api_key=config['api_key'],
    project_id=config.get('project_id', 'default')
)

# 发送邮件
response = client.send_email(
    to='recipient@example.com',
    subject='测试邮件',
    body_text='邮件内容'
)
""")
    
    print("\n2. 环境变量方式:")
    print("""
export HYVOR_RELAY_URL=http://localhost:8080
export HYVOR_RELAY_API_KEY=your_api_key
export HYVOR_RELAY_PROJECT_ID=default
export HYVOR_RELAY_FROM_EMAIL=noreply@yourdomain.com

# Python 代码中会自动读取环境变量
from hyvor_relay.client import HyvorRelayClient
client = HyvorRelayClient()  # 自动使用环境变量
""")
    
    print("\n3. 常用命令:")
    print(f"   查看配置: {sys.argv[0]} --show")
    print(f"   测试连接: {sys.argv[0]} --test")
    print(f"   发送测试: {sys.argv[0]} --send-test")
    print(f"   快速配置: {sys.argv[0]} --quick")
    
    print("\n🎉 配置完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        sys.exit(1)
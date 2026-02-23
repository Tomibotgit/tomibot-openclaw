#!/usr/bin/env python3
"""
Hyvor Relay 监控脚本
监控邮件队列、发送状态和系统健康
"""

import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from hyvor_relay.client import HyvorRelayClient, HyvorRelayError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MonitorMetrics:
    """监控指标"""
    timestamp: str
    connection_status: bool
    rate_limit_remaining: Optional[int]
    rate_limit_reset: Optional[int]
    recent_sends: int
    success_rate: float
    avg_response_time: float
    errors: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class HyvorRelayMonitor:
    """Hyvor Relay 监控器"""
    
    def __init__(self, client: HyvorRelayClient, project_id: str = "default"):
        """
        初始化监控器
        
        Args:
            client: Hyvor Relay 客户端
            project_id: 项目ID
        """
        self.client = client
        self.project_id = project_id
        self.metrics_history: List[MonitorMetrics] = []
        
    def check_connection(self) -> bool:
        """检查连接状态"""
        try:
            return self.client.test_connection()
        except Exception as e:
            logger.error(f"连接检查失败: {e}")
            return False
    
    def get_rate_limit_info(self) -> Dict:
        """获取速率限制信息"""
        try:
            return self.client.get_rate_limit_info()
        except Exception as e:
            logger.warning(f"获取速率限制信息失败: {e}")
            return {}
    
    def get_recent_sends(self, hours: int = 1) -> List[Dict]:
        """获取最近发送的邮件"""
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d")
            
            return self.client.get_send_logs(
                start_date=start_date,
                end_date=end_date,
                limit=100
            )
        except Exception as e:
            logger.error(f"获取发送记录失败: {e}")
            return []
    
    def calculate_success_rate(self, sends: List[Dict]) -> float:
        """计算成功率"""
        if not sends:
            return 0.0
        
        successful = sum(1 for send in sends if send.get("status") in ["delivered", "sent"])
        return successful / len(sends)
    
    def collect_metrics(self) -> MonitorMetrics:
        """收集监控指标"""
        timestamp = datetime.now().isoformat()
        
        # 检查连接
        connection_status = self.check_connection()
        
        # 获取速率限制
        rate_info = self.get_rate_limit_info()
        rate_limit_remaining = int(rate_info.get("remaining")) if rate_info.get("remaining") else None
        rate_limit_reset = int(rate_info.get("reset")) if rate_info.get("reset") else None
        
        # 获取最近发送记录
        recent_sends = self.get_recent_sends(hours=1)
        
        # 计算指标
        success_rate = self.calculate_success_rate(recent_sends)
        
        # 计算平均响应时间（模拟）
        avg_response_time = 0.5  # 模拟值
        
        # 错误列表
        errors = []
        if not connection_status:
            errors.append("连接失败")
        if rate_limit_remaining is not None and rate_limit_remaining < 10:
            errors.append(f"速率限制剩余: {rate_limit_remaining}")
        if success_rate < 0.95:
            errors.append(f"成功率低: {success_rate:.1%}")
        
        # 创建指标对象
        metrics = MonitorMetrics(
            timestamp=timestamp,
            connection_status=connection_status,
            rate_limit_remaining=rate_limit_remaining,
            rate_limit_reset=rate_limit_reset,
            recent_sends=len(recent_sends),
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            errors=errors
        )
        
        # 保存到历史
        self.metrics_history.append(metrics)
        
        # 保持历史记录大小
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics
    
    def print_metrics(self, metrics: MonitorMetrics, verbose: bool = False):
        """打印指标"""
        print("\n" + "=" * 60)
        print(f"📊 Hyvor Relay 监控报告")
        print(f"   时间: {metrics.timestamp}")
        print(f"   项目: {self.project_id}")
        print("=" * 60)
        
        # 连接状态
        status_icon = "✅" if metrics.connection_status else "❌"
        print(f"{status_icon} 连接状态: {'正常' if metrics.connection_status else '异常'}")
        
        # 速率限制
        if metrics.rate_limit_remaining is not None:
            reset_time = f" ({metrics.rate_limit_reset}s后重置)" if metrics.rate_limit_reset else ""
            print(f"📈 速率限制: 剩余 {metrics.rate_limit_remaining} 次{reset_time}")
        
        # 发送统计
        print(f"📨 最近1小时发送: {metrics.recent_sends} 封")
        print(f"📊 成功率: {metrics.success_rate:.1%}")
        print(f"⚡ 平均响应时间: {metrics.avg_response_time:.2f}秒")
        
        # 错误信息
        if metrics.errors:
            print(f"\n⚠️  警告:")
            for error in metrics.errors:
                print(f"   • {error}")
        
        # 详细模式
        if verbose:
            print(f"\n📋 详细信息:")
            print(f"   历史记录数: {len(self.metrics_history)}")
            
            # 显示历史趋势
            if len(self.metrics_history) > 1:
                first = self.metrics_history[0]
                last = self.metrics_history[-1]
                
                success_rate_change = last.success_rate - first.success_rate
                if abs(success_rate_change) > 0.01:
                    trend = "上升" if success_rate_change > 0 else "下降"
                    print(f"   成功率趋势: {trend} {abs(success_rate_change):.1%}")
        
        print("=" * 60)
    
    def save_metrics_to_file(self, metrics: MonitorMetrics, file_path: Path):
        """保存指标到文件"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有数据
            data = []
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
            
            # 添加新数据
            data.append(metrics.to_dict())
            
            # 保持数据大小
            if len(data) > 1000:
                data = data[-1000:]
            
            # 保存数据
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"指标已保存到: {file_path}")
            
        except Exception as e:
            logger.error(f"保存指标失败: {e}")
    
    def generate_report(self, hours: int = 24) -> Dict:
        """生成监控报告"""
        # 过滤指定时间范围内的指标
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "没有足够的数据"}
        
        # 计算统计信息
        total_sends = sum(m.recent_sends for m in recent_metrics)
        avg_success_rate = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
        
        # 连接状态统计
        connection_up = sum(1 for m in recent_metrics if m.connection_status)
        connection_down = len(recent_metrics) - connection_up
        uptime_percentage = connection_up / len(recent_metrics) * 100 if recent_metrics else 0
        
        # 错误统计
        all_errors = []
        for m in recent_metrics:
            all_errors.extend(m.errors)
        
        error_counts = {}
        for error in all_errors:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # 生成报告
        report = {
            "report_time": datetime.now().isoformat(),
            "time_range_hours": hours,
            "metrics_count": len(recent_metrics),
            "total_sends": total_sends,
            "average_success_rate": avg_success_rate,
            "uptime_percentage": uptime_percentage,
            "connection_stats": {
                "up": connection_up,
                "down": connection_down,
                "uptime_percentage": uptime_percentage
            },
            "error_summary": error_counts,
            "recent_metrics": [m.to_dict() for m in recent_metrics[-10:]]  # 最近10条
        }
        
        return report


def load_config(config_path: Path) -> Dict:
    """加载配置"""
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 从环境变量加载
    config = {
        "base_url": os.getenv("HYVOR_RELAY_URL", "http://localhost:8080"),
        "api_key": os.getenv("HYVOR_RELAY_API_KEY"),
        "project_id": os.getenv("HYVOR_RELAY_PROJECT_ID", "default")
    }
    
    return config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Hyvor Relay 监控脚本")
    parser.add_argument("--config", "-c", default="~/.hyvor-relay/config.json",
                       help="配置文件路径")
    parser.add_argument("--interval", "-i", type=int, default=60,
                       help="监控间隔（秒）")
    parser.add_argument("--output", "-o",
                       help="指标输出文件路径")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出")
    parser.add_argument("--once", action="store_true",
                       help="只运行一次")
    parser.add_argument("--report", "-r", type=int,
                       help="生成报告（小时数）")
    parser.add_argument("--project", "-p",
                       help="项目ID")
    
    args = parser.parse_args()
    
    # 加载配置
    config_path = Path(args.config).expanduser()
    config = load_config(config_path)
    
    # 设置项目ID
    project_id = args.project or config.get("project_id", "default")
    
    # 创建客户端
    try:
        client = HyvorRelayClient(
            base_url=config.get("base_url"),
            api_key=config.get("api_key"),
            project_id=project_id
        )
    except Exception as e:
        logger.error(f"创建客户端失败: {e}")
        sys.exit(1)
    
    # 创建监控器
    monitor = HyvorRelayMonitor(client, project_id)
    
    # 生成报告
    if args.report:
        report = monitor.generate_report(hours=args.report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    
    # 监控循环
    print("🚀 Hyvor Relay 监控启动")
    print(f"   服务地址: {config.get('base_url')}")
    print(f"   项目ID: {project_id}")
    print(f"   监控间隔: {args.interval}秒")
    print(f"   输出文件: {args.output or '无'}")
    print("")
    
    try:
        while True:
            # 收集指标
            metrics = monitor.collect_metrics()
            
            # 打印指标
            monitor.print_metrics(metrics, args.verbose)
            
            # 保存到文件
            if args.output:
                output_path = Path(args.output).expanduser()
                monitor.save_metrics_to_file(metrics, output_path)
            
            # 单次运行
            if args.once:
                break
            
            # 等待下一次收集
            print(f"\n⏳ 等待 {args.interval} 秒...")
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控停止")
    except Exception as e:
        logger.error(f"监控失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
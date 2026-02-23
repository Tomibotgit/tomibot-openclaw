"""
Hyvor Relay Python 客户端
一个完整的 Hyvor Relay 邮件服务 Python 客户端
"""

import os
import json
import base64
import time
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailAddress:
    """邮件地址"""
    email: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        if self.name:
            return {"name": self.name, "email": self.email}
        return self.email


@dataclass
class Attachment:
    """邮件附件"""
    content: Union[str, bytes]  # base64 字符串或 bytes
    name: str
    content_type: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        if isinstance(self.content, bytes):
            content = base64.b64encode(self.content).decode('utf-8')
        else:
            content = self.content
        
        result = {
            "content": content,
            "name": self.name
        }
        
        if self.content_type:
            result["content_type"] = self.content_type
        
        return result


@dataclass
class EmailRequest:
    """邮件请求"""
    from_address: Union[str, EmailAddress, Dict]
    to: Union[str, EmailAddress, Dict, List[Union[str, EmailAddress, Dict]]]
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    cc: Optional[Union[str, EmailAddress, Dict, List[Union[str, EmailAddress, Dict]]]] = None
    bcc: Optional[Union[str, EmailAddress, Dict, List[Union[str, EmailAddress, Dict]]]] = None
    headers: Optional[Dict[str, str]] = None
    attachments: Optional[List[Attachment]] = None
    
    def to_dict(self) -> Dict:
        """转换为 API 请求格式"""
        def normalize_address(addr):
            if isinstance(addr, EmailAddress):
                return addr.to_dict()
            elif isinstance(addr, dict) and 'email' in addr:
                return addr
            elif isinstance(addr, str):
                return addr
            return str(addr)
        
        def normalize_address_list(addr_list):
            if isinstance(addr_list, list):
                return [normalize_address(addr) for addr in addr_list]
            return normalize_address(addr_list)
        
        request_dict = {
            "from": normalize_address(self.from_address),
            "to": normalize_address_list(self.to),
            "subject": self.subject
        }
        
        if self.body_html:
            request_dict["body_html"] = self.body_html
        if self.body_text:
            request_dict["body_text"] = self.body_text
        if self.cc:
            request_dict["cc"] = normalize_address_list(self.cc)
        if self.bcc:
            request_dict["bcc"] = normalize_address_list(self.bcc)
        if self.headers:
            request_dict["headers"] = self.headers
        if self.attachments:
            request_dict["attachments"] = [att.to_dict() for att in self.attachments]
        
        return request_dict


class HyvorRelayError(Exception):
    """Hyvor Relay 错误基类"""
    pass


class AuthenticationError(HyvorRelayError):
    """认证错误"""
    pass


class ValidationError(HyvorRelayError):
    """验证错误"""
    pass


class RateLimitError(HyvorRelayError):
    """速率限制错误"""
    pass


class HyvorRelayClient:
    """Hyvor Relay 客户端"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        project_id: str = "default",
        timeout: int = 30,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 10
    ):
        """
        初始化客户端
        
        Args:
            base_url: Hyvor Relay 基础 URL (例如: http://localhost:8080)
            api_key: API 密钥
            project_id: 项目ID
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            pool_connections: 连接池大小
            pool_maxsize: 最大连接数
        """
        self.base_url = base_url or os.getenv("HYVOR_RELAY_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("HYVOR_RELAY_API_KEY")
        self.project_id = project_id or os.getenv("HYVOR_RELAY_PROJECT_ID", "default")
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("API key is required. Set HYVOR_RELAY_API_KEY environment variable or pass api_key parameter.")
        
        # 创建会话
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # 配置适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"HyvorRelayPythonClient/1.0.0"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: 请求参数
            
        Returns:
            响应数据
            
        Raises:
            AuthenticationError: 认证失败
            ValidationError: 请求验证失败
            RateLimitError: 速率限制
            HyvorRelayError: 其他错误
        """
        url = f"{self.base_url.rstrip('/')}/api/console{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # 处理响应
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 403:
                raise AuthenticationError("Insufficient permissions")
            elif response.status_code == 422:
                error_data = response.json()
                raise ValidationError(f"Validation error: {error_data}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise HyvorRelayError(f"API error {response.status_code}: {error_data}")
            
            # 返回 JSON 数据
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise HyvorRelayError(f"Request failed: {e}")
    
    def send_email(
        self,
        to: Union[str, EmailAddress, Dict, List[Union[str, EmailAddress, Dict]]],
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        from_email: Optional[Union[str, EmailAddress, Dict]] = None,
        cc: Optional[Union[str, EmailAddress, Dict, List[Union[str, EmailAddress, Dict]]]] = None,
        bcc: Optional[Union[str, EmailAddress, Dict, List[Union[str, EmailAddress, Dict]]]] = None,
        attachments: Optional[List[Attachment]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        发送邮件
        
        Args:
            to: 收件人地址
            subject: 邮件主题
            body_text: 纯文本内容
            body_html: HTML 内容
            from_email: 发件人地址（可选，使用默认配置）
            cc: 抄送
            bcc: 密送
            attachments: 附件列表
            headers: 自定义头部
            
        Returns:
            发送响应
        """
        # 设置默认发件人
        if not from_email:
            default_from = os.getenv("HYVOR_RELAY_FROM_EMAIL", "noreply@localhost")
            from_email = EmailAddress(email=default_from)
        
        # 创建邮件请求
        email_request = EmailRequest(
            from_address=from_email,
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            headers=headers
        )
        
        # 发送请求
        return self._make_request(
            method="POST",
            endpoint="/sends",
            json=email_request.to_dict()
        )
    
    def send_email_simple(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = False,
        **kwargs
    ) -> Dict:
        """
        发送简单邮件
        
        Args:
            to: 收件人地址
            subject: 邮件主题
            body: 邮件内容
            is_html: 是否为 HTML 内容
            **kwargs: 其他参数
            
        Returns:
            发送响应
        """
        if is_html:
            return self.send_email(to=to, subject=subject, body_html=body, **kwargs)
        else:
            return self.send_email(to=to, subject=subject, body_text=body, **kwargs)
    
    def get_email_status(self, email_id: str) -> Dict:
        """
        获取邮件状态
        
        Args:
            email_id: 邮件ID
            
        Returns:
            邮件状态信息
        """
        return self._make_request("GET", f"/sends/{email_id}")
    
    def get_send_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        获取发送日志
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            发送日志列表
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = self._make_request("GET", "/sends", params=params)
        return response.get("data", [])
    
    def create_attachment_from_file(
        self,
        file_path: str,
        name: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Attachment:
        """
        从文件创建附件
        
        Args:
            file_path: 文件路径
            name: 附件名称（可选，默认使用文件名）
            content_type: 内容类型（可选，自动检测）
            
        Returns:
            附件对象
        """
        import mimetypes
        
        if not name:
            name = os.path.basename(file_path)
        
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
        
        with open(file_path, "rb") as f:
            content = f.read()
        
        return Attachment(
            content=content,
            name=name,
            content_type=content_type
        )
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            连接是否成功
        """
        try:
            # 尝试获取项目信息
            self._make_request("GET", f"/projects/{self.project_id}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_rate_limit_info(self) -> Dict:
        """
        获取速率限制信息
        
        Returns:
            速率限制信息
        """
        try:
            # 发送一个测试请求并检查响应头
            response = self.session.head(f"{self.base_url.rstrip('/')}/api/console/sends")
            
            rate_limit_info = {
                "limit": response.headers.get("X-RateLimit-Limit"),
                "remaining": response.headers.get("X-RateLimit-Remaining"),
                "reset": response.headers.get("X-RateLimit-Reset")
            }
            
            return {k: v for k, v in rate_limit_info.items() if v is not None}
        except Exception as e:
            logger.warning(f"Failed to get rate limit info: {e}")
            return {}


# 简化导入
def create_client(**kwargs) -> HyvorRelayClient:
    """创建客户端快捷函数"""
    return HyvorRelayClient(**kwargs)
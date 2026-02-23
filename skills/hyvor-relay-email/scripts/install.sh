#!/bin/bash

# Hyvor Relay 安装脚本
# 安装和配置 Hyvor Relay 邮件服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 显示帮助
show_help() {
    echo "Hyvor Relay 安装脚本"
    echo ""
    echo "用法: $0 [选项] [安装路径]"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -d, --docker    使用 Docker 安装（默认）"
    echo "  -s, --source    从源码安装"
    echo "  -t, --test      安装后运行测试"
    echo "  -c, --configure 交互式配置"
    echo ""
    echo "示例:"
    echo "  $0 /opt/hyvor-relay          # 安装到指定目录"
    echo "  $0 --docker                   # 使用 Docker 安装"
    echo "  $0 --test                     # 安装并测试"
}

# 安装依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 检测系统类型
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
    else
        OS=$(uname -s)
    fi
    
    case $OS in
        *Ubuntu*|*Debian*)
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                wget \
                git \
                docker.io \
                docker-compose \
                python3 \
                python3-pip \
                python3-venv
            ;;
        *CentOS*|*RedHat*|*Fedora*)
            sudo yum install -y \
                curl \
                wget \
                git \
                docker \
                docker-compose \
                python3 \
                python3-pip
            ;;
        *Darwin*)  # macOS
            if ! command -v brew &> /dev/null; then
                log_error "请先安装 Homebrew: https://brew.sh/"
                exit 1
            fi
            brew install \
                curl \
                wget \
                git \
                docker \
                docker-compose \
                python3
            ;;
        *)
            log_warning "未知操作系统: $OS"
            log_info "请手动安装以下依赖:"
            log_info "  - curl/wget"
            log_info "  - git"
            log_info "  - Docker"
            log_info "  - Docker Compose"
            log_info "  - Python 3"
            ;;
    esac
    
    log_success "依赖安装完成"
}

# Docker 安装方式
install_with_docker() {
    log_info "使用 Docker 安装 Hyvor Relay..."
    
    # 创建目录
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # 克隆仓库
    if [[ ! -d "relay" ]]; then
        git clone https://github.com/hyvor/relay.git
    fi
    
    cd relay
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请启动 Docker 服务"
        exit 1
    fi
    
    # 启动服务
    log_info "启动 Hyvor Relay 服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "Hyvor Relay 服务已启动"
        
        # 显示服务信息
        echo ""
        log_info "服务信息:"
        echo "  - Web 界面: http://localhost:8080"
        echo "  - API 地址: http://localhost:8080/api"
        echo "  - 控制台: http://localhost:8080/console"
        echo ""
        log_info "使用以下命令管理服务:"
        echo "  cd $INSTALL_DIR/relay"
        echo "  docker-compose logs -f      # 查看日志"
        echo "  docker-compose restart      # 重启服务"
        echo "  docker-compose down         # 停止服务"
    else
        log_error "服务启动失败，请检查日志"
        docker-compose logs
        exit 1
    fi
}

# 源码安装方式
install_from_source() {
    log_info "从源码安装 Hyvor Relay..."
    
    # 创建目录
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # 克隆仓库
    if [[ ! -d "relay" ]]; then
        git clone https://github.com/hyvor/relay.git
    fi
    
    cd relay
    
    # 安装开发环境
    log_info "安装开发环境..."
    if [[ -f "run" ]]; then
        chmod +x run
        ./run setup
    else
        log_warning "未找到开发脚本，请参考官方文档"
    fi
    
    log_success "源码安装完成"
    log_info "请参考官方文档启动服务: https://relay.hyvor.com/hosting"
}

# 配置环境
configure_environment() {
    log_info "配置环境..."
    
    # 创建配置文件目录
    CONFIG_DIR="$HOME/.hyvor-relay"
    mkdir -p "$CONFIG_DIR"
    
    # 交互式配置
    echo ""
    log_info "请输入 Hyvor Relay 配置信息:"
    echo ""
    
    read -p "Hyvor Relay URL [http://localhost:8080]: " RELAY_URL
    RELAY_URL=${RELAY_URL:-"http://localhost:8080"}
    
    read -p "API Key (留空稍后配置): " API_KEY
    
    read -p "默认发件人邮箱 [noreply@localhost]: " FROM_EMAIL
    FROM_EMAIL=${FROM_EMAIL:-"noreply@localhost"}
    
    read -p "默认项目ID [default]: " PROJECT_ID
    PROJECT_ID=${PROJECT_ID:-"default"}
    
    # 创建配置文件
    cat > "$CONFIG_DIR/config.env" << EOF
# Hyvor Relay 配置
HYVOR_RELAY_URL=$RELAY_URL
HYVOR_RELAY_API_KEY=$API_KEY
HYVOR_RELAY_PROJECT_ID=$PROJECT_ID
HYVOR_RELAY_FROM_EMAIL=$FROM_EMAIL
EOF
    
    # 创建 Python 客户端配置
    cat > "$CONFIG_DIR/client_config.py" << EOF
# Hyvor Relay Python 客户端配置
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("$CONFIG_DIR/config.env")

# 客户端配置
HYVOR_RELAY_CONFIG = {
    "base_url": os.getenv("HYVOR_RELAY_URL", "http://localhost:8080"),
    "api_key": os.getenv("HYVOR_RELAY_API_KEY"),
    "project_id": os.getenv("HYVOR_RELAY_PROJECT_ID", "default"),
    "default_from_email": os.getenv("HYVOR_RELAY_FROM_EMAIL", "noreply@localhost")
}
EOF
    
    # 创建 bash 配置文件
    cat > "$CONFIG_DIR/hyvor-relay.sh" << EOF
# Hyvor Relay 环境变量
export HYVOR_RELAY_URL="$RELAY_URL"
export HYVOR_RELAY_PROJECT_ID="$PROJECT_ID"
export HYVOR_RELAY_FROM_EMAIL="$FROM_EMAIL"

if [ -n "$API_KEY" ]; then
    export HYVOR_RELAY_API_KEY="$API_KEY"
fi

# 快捷命令
alias hyvor-relay-status="docker-compose -f $INSTALL_DIR/relay/docker-compose.yml ps"
alias hyvor-relay-logs="docker-compose -f $INSTALL_DIR/relay/docker-compose.yml logs -f"
alias hyvor-relay-restart="docker-compose -f $INSTALL_DIR/relay/docker-compose.yml restart"
alias hyvor-relay-stop="docker-compose -f $INSTALL_DIR/relay/docker-compose.yml down"
alias hyvor-relay-start="docker-compose -f $INSTALL_DIR/relay/docker-compose.yml up -d"
EOF
    
    # 添加到 bashrc
    if ! grep -q "hyvor-relay.sh" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# Hyvor Relay 配置" >> "$HOME/.bashrc"
        echo "source $CONFIG_DIR/hyvor-relay.sh" >> "$HOME/.bashrc"
        log_info "已将配置添加到 ~/.bashrc"
    fi
    
    if [[ -f "$HOME/.zshrc" ]] && ! grep -q "hyvor-relay.sh" "$HOME/.zshrc" 2>/dev/null; then
        echo "" >> "$HOME/.zshrc"
        echo "# Hyvor Relay 配置" >> "$HOME/.zshrc"
        echo "source $CONFIG_DIR/hyvor-relay.sh" >> "$HOME/.zshrc"
        log_info "已将配置添加到 ~/.zshrc"
    fi
    
    log_success "环境配置完成"
    log_info "配置文件位置: $CONFIG_DIR/"
    
    if [[ -z "$API_KEY" ]]; then
        echo ""
        log_warning "请获取 API Key 后添加到配置文件:"
        echo "  1. 访问: $RELAY_URL/console"
        echo "  2. 创建项目并获取 API Key"
        echo "  3. 编辑: $CONFIG_DIR/config.env"
        echo "  4. 设置 HYVOR_RELAY_API_KEY=your_api_key"
    fi
}

# 安装 Python 客户端
install_python_client() {
    log_info "安装 Python 客户端..."
    
    # 创建虚拟环境
    VENV_DIR="$INSTALL_DIR/venv"
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    # 激活虚拟环境并安装
    source "$VENV_DIR/bin/activate"
    
    # 安装依赖
    pip install --upgrade pip
    pip install \
        requests \
        python-dotenv \
        pydantic \
        typing-extensions
    
    # 安装客户端包
    CLIENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    pip install -e "$CLIENT_DIR"
    
    deactivate
    
    log_success "Python 客户端安装完成"
    log_info "虚拟环境位置: $VENV_DIR"
    log_info "激活虚拟环境: source $VENV_DIR/bin/activate"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 检查服务是否运行
    if ! curl -s "http://localhost:8080/health" &> /dev/null; then
        log_warning "Hyvor Relay 服务未运行，跳过测试"
        return
    fi
    
    # 激活虚拟环境
    source "$INSTALL_DIR/venv/bin/activate"
    
    # 运行测试脚本
    TEST_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/test_connection.py"
    
    if [[ -f "$TEST_SCRIPT" ]]; then
        python "$TEST_SCRIPT"
    else
        # 创建简单测试
        cat > /tmp/test_hyvor.py << 'EOF'
#!/usr/bin/env python3
"""测试 Hyvor Relay 连接"""

import os
import sys
from hyvor_relay.client import HyvorRelayClient

def test_connection():
    """测试连接"""
    try:
        # 从环境变量获取配置
        base_url = os.getenv("HYVOR_RELAY_URL", "http://localhost:8080")
        api_key = os.getenv("HYVOR_RELAY_API_KEY")
        
        if not api_key:
            print("❌ 未设置 API Key，请设置 HYVOR_RELAY_API_KEY 环境变量")
            print("   或在配置文件中设置")
            return False
        
        # 创建客户端
        client = HyvorRelayClient(base_url=base_url, api_key=api_key)
        
        # 测试连接
        if client.test_connection():
            print("✅ 连接成功")
            
            # 测试速率限制
            rate_info = client.get_rate_limit_info()
            if rate_info:
                print(f"📊 速率限制信息:")
                for key, value in rate_info.items():
                    print(f"   {key}: {value}")
            
            return True
        else:
            print("❌ 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 测试 Hyvor Relay 连接...")
    print(f"   服务地址: {os.getenv('HYVOR_RELAY_URL', 'http://localhost:8080')}")
    print("")
    
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
EOF
        
        python /tmp/test_hyvor.py
        rm /tmp/test_hyvor.py
    fi
    
    deactivate
}

# 主函数
main() {
    # 默认值
    INSTALL_MODE="docker"
    INSTALL_DIR="/opt/hyvor-relay"
    DO_CONFIGURE=false
    DO_TEST=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--docker)
                INSTALL_MODE="docker"
                shift
                ;;
            -s|--source)
                INSTALL_MODE="source"
                shift
                ;;
            -t|--test)
                DO_TEST=true
                shift
                ;;
            -c|--configure)
                DO_CONFIGURE=true
                shift
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                INSTALL_DIR="$1"
                shift
                ;;
        esac
    done
    
    # 显示标题
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          Hyvor Relay 安装脚本                        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_info "安装模式: $INSTALL_MODE"
    log_info "安装目录: $INSTALL_DIR"
    
    # 检查依赖
    check_command curl
    check_command git
    
    if [[ "$INSTALL_MODE" == "docker" ]]; then
        check_command docker
        check_command docker-compose
    fi
    
    check_command python3
    
    # 安装依赖
    install_dependencies
    
    # 执行安装
    case $INSTALL_MODE in
        "docker")
            install_with_docker
            ;;
        "source")
            install_from_source
            ;;
    esac
    
    # 安装 Python 客户端
    install_python_client
    
    # 配置环境
    if $DO_CONFIGURE; then
        configure_environment
    fi
    
    # 运行测试
    if $DO_TEST; then
        run_tests
    fi
    
    # 完成信息
    echo ""
    log_success "安装完成！"
    echo ""
    log_info "下一步:"
    echo "  1. 访问控制台: http://localhost:8080/console"
    echo "  2. 创建项目和 API Key"
    echo "  3. 配置环境变量（运行: $0 --configure）"
    echo "  4. 开始使用 Python 客户端发送邮件"
    echo ""
    log_info "Python 客户端使用示例:"
    echo "  from hyvor_relay.client import HyvorRelayClient"
    echo "  client = HyvorRelayClient()"
    echo "  client.send_email(to='test@example.com', subject='测试', body='内容')"
    echo ""
}

# 运行主函数
main "$@"
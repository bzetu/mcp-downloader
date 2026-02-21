# mcp-downloader

MCP 下载工具集 - 支持 URL 下载、SCP 文件传输、Git 克隆

## 功能

| 工具 | 功能 | 说明 |
|------|------|------|
| `download_url` | HTTP/HTTPS 下载 | 从 URL 下载文件到本地 |
| `download_scp` | SCP 文件传输 | 从远程服务器下载文件（用户名+密码认证）|
| `git_clone` | Git 仓库克隆 | 克隆 Git 仓库到本地 |

## 特性

- ✅ 阻塞式下载（一次一个，等待完成）
- ✅ MCP 失败时返回错误信息，引导使用 bash 替代
- ✅ 参数传递认证信息（不存储密码）
- ✅ 跨 MCP 兼容客户端使用

## 安装

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/mcp-downloader.git
cd mcp-downloader

# 2. 以可编辑模式安装（推荐）
# 这样 Python 能直接找到 mcp_downloader 模块，无需手动配置 PYTHONPATH
pip install -e .

# 或使用 uv（推荐）
uv venv
uv pip install -e .
```

## OpenCode 配置

在 `opencode.json` 中添加：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "mcp-downloader": {
      "type": "local",
      "command": ["python3", "-m", "mcp_downloader"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-downloader"
      },
      "enabled": true
    }
  }
}
```

注意：将 `/path/to/mcp-downloader` 替换为你的实际项目路径。

## AGENTS.md 引导规则

将以下内容添加到项目的 `AGENTS.md` 或全局 `~/.config/opencode/AGENTS.md`：

```markdown
# 文件下载规则

当需要下载文件时，优先使用 MCP 工具 `mcp-downloader`：
- URL 下载 → 使用 download_url 工具
- 远程服务器文件下载 → 使用 download_scp 工具
- Git 仓库克隆 → 使用 git_clone 工具

如果 mcp-downloader MCP 工具调用失败（连接超时、认证失败等），
请使用 bash 命令作为替代方案：
- URL 下载：使用 curl 或 wget 命令
- SCP 下载：使用 scp 命令
- Git 克隆：使用 git clone 命令
```

## 其他 MCP 客户端配置

此工具兼容所有支持 MCP 协议的 AI 工具。

### Cursor

在 `.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "mcp-downloader": {
      "command": "python3",
      "args": ["-m", "mcp_downloader"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-downloader"
      }
    }
  }
}
```

### Claude Desktop

在 `~/Library/Application Support/Claude/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "mcp-downloader": {
      "command": "python3",
      "args": ["-m", "mcp_downloader"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-downloader"
      }
    }
  }
}
```

### Claude Code

在 `~/.config/claude/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "mcp-downloader": {
      "command": "python3",
      "args": ["-m", "mcp_downloader"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-downloader"
      }
    }
  }
}
```

## 使用示例

### URL 下载

> 下载 https://example.com/file.zip 到 ~/Downloads

参数：
- `url`: https://example.com/file.zip
- `path`: ~/Downloads

### SCP 下载

> 从 192.168.1.100 用户名 admin 密码 123 下载 /data/file.zip 到 ~/Downloads

参数：
- `host`: 192.168.1.100
- `remote_path`: /data/file.zip
- `local_path`: ~/Downloads
- `port`: 22（可选，默认 22）
- `username`: admin
- `password`: 123

### Git 克隆

> 克隆 https://github.com/user/repo 到 ~/code/repo

参数：
- `url`: https://github.com/user/repo
- `path`: ~/code/repo
- `branch`: main（可选）

## 本地测试

```bash
# 测试 MCP 服务器
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | \
  PYTHONPATH=/path/to/mcp-downloader python3 -m mcp_downloader

# 测试下载工具
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"download_url","arguments":{"url":"https://example.com/file.zip","path":"~/Downloads"}}}' | \
  PYTHONPATH=/path/to/mcp-downloader python3 -m mcp_downloader
```

## 依赖

- paramiko>=3.0.0
- requests>=2.31.0

## 许可证

MIT

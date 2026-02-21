import os
import subprocess
from pathlib import Path


def git_clone(url: str, path: str = ".", branch: str = None) -> dict:
    """
    Clone Git repositories

    Args:
        url: Git repository URL
        path: Local directory to clone into (default: current directory)
        branch: Branch to clone (default: default branch)

    Returns:
        dict with success status and details
    """
    try:
        path = os.path.expanduser(path)

        repo_name = Path(url.split("/")[-1]).stem
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        target_path = os.path.join(path, repo_name) if path != "." else repo_name

        if os.path.exists(target_path):
            return {
                "success": False,
                "error": f"目录已存在: {target_path}",
                "suggestion": "请尝试使用 git pull 命令更新，或删除现有目录后重试",
            }

        cmd = ["git", "clone"]
        if branch:
            cmd.extend(["--branch", branch])
        cmd.extend([url, target_path])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Successfully cloned {repo_name}",
                "repo_path": target_path,
                "url": url,
                "branch": branch or "default",
            }
        else:
            error_msg = result.stderr
            if "Authentication failed" in error_msg or "Permission denied" in error_msg:
                return {
                    "success": False,
                    "error": "认证失败：可能需要用户名和密码",
                    "suggestion": "请尝试使用 git clone 命令手动克隆，或配置 Git 凭证",
                }
            return {
                "success": False,
                "error": f"Git clone failed: {error_msg}",
                "suggestion": "请尝试使用 git clone 命令手动克隆",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "克隆超时",
            "suggestion": "请尝试使用 git clone 命令手动克隆，或检查网络连接",
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Git 未安装",
            "suggestion": "请先安装 Git，或使用 git clone 命令手动克隆",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "suggestion": "请尝试使用 git clone 命令手动克隆",
        }

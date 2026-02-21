import os
import paramiko
from pathlib import Path

from mcp_downloader.utils.stop_flag import is_stopped


def download_scp(
    host: str,
    port: int,
    username: str,
    password: str,
    remote_path: str,
    local_path: str = "~/Downloads",
) -> dict:
    """
    Download files from remote servers via SCP

    Args:
        host: Remote server IP or hostname
        port: SSH port (default: 22)
        username: SSH username
        password: SSH password
        remote_path: Path to the remote file
        local_path: Local directory to save the file (default: ~/Downloads)

    Returns:
        dict with success status and details
    """
    ssh = None
    sftp = None
    local_file = None

    try:
        if not host:
            return {
                "success": False,
                "error": "服务器地址不能为空",
                "suggestion": "请提供远程服务器的 IP 地址或主机名",
            }

        if not remote_path:
            return {
                "success": False,
                "error": "远程文件路径不能为空",
                "suggestion": "请提供远程服务器上的文件完整路径",
            }

        if not username or not password:
            return {
                "success": False,
                "error": "用户名和密码为必填参数",
                "suggestion": "请提供用户名和密码，或尝试使用 scp 命令手动下载",
            }

        local_path = os.path.expanduser(local_path)
        os.makedirs(local_path, exist_ok=True)

        filename = Path(remote_path).name
        if not filename:
            filename = "downloaded_file"

        local_file = os.path.join(local_path, filename)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            hostname=host, port=port, username=username, password=password, timeout=30
        )

        sftp = ssh.open_sftp()

        file_size = sftp.stat(remote_path).st_size
        downloaded = 0

        with sftp.file(remote_path, "r") as remote_file:
            with open(local_file, "wb") as f:
                while True:
                    if is_stopped():
                        f.close()
                        if os.path.exists(local_file):
                            os.remove(local_file)
                        return {
                            "success": False,
                            "error": "下载已取消",
                            "cancelled": True,
                            "host": host,
                            "remote_path": remote_path,
                        }
                    chunk = remote_file.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

        sftp.close()
        ssh.close()

        return {
            "success": True,
            "message": f"Successfully downloaded {filename}",
            "file_path": local_file,
            "file_size": downloaded,
            "host": host,
            "remote_path": remote_path,
        }

    except paramiko.AuthenticationException:
        if sftp:
            try:
                sftp.close()
            except:
                pass
        if ssh:
            ssh.close()
        if local_file and os.path.exists(local_file):
            os.remove(local_file)
        return {
            "success": False,
            "error": "认证失败：用户名或密码错误",
            "suggestion": "请检查用户名和密码是否正确，或尝试使用 scp 命令手动下载",
        }
    except paramiko.SSHException as e:
        if sftp:
            try:
                sftp.close()
            except:
                pass
        if ssh:
            ssh.close()
        if local_file and os.path.exists(local_file):
            os.remove(local_file)
        return {
            "success": False,
            "error": f"SSH 连接失败: {str(e)}",
            "suggestion": "请检查服务器地址和端口是否正确，或尝试使用 scp 命令手动下载",
        }
    except FileNotFoundError:
        if sftp:
            try:
                sftp.close()
            except:
                pass
        if ssh:
            ssh.close()
        return {
            "success": False,
            "error": f"远程文件不存在: {remote_path}",
            "suggestion": "请检查远程文件路径是否正确",
        }
    except Exception as e:
        if sftp:
            try:
                sftp.close()
            except:
                pass
        if ssh:
            ssh.close()
        if local_file and os.path.exists(local_file):
            os.remove(local_file)
        return {
            "success": False,
            "error": f"下载失败: {str(e)}",
            "suggestion": "请尝试使用 scp 命令手动下载",
        }

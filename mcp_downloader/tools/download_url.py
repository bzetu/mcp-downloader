import os
import requests
from pathlib import Path
from urllib.parse import urlparse

from mcp_downloader.utils.stop_flag import is_stopped


def download_url(url: str, path: str = "~/Downloads") -> dict:
    """
    Download files from HTTP/HTTPS URLs

    Args:
        url: The URL to download from
        path: Local directory to save the file (default: ~/Downloads)

    Returns:
        dict with success status and details
    """
    try:
        path = os.path.expanduser(path)
        os.makedirs(path, exist_ok=True)

        filename = Path(urlparse(url).path).name
        if not filename:
            filename = "downloaded_file"

        local_file = os.path.join(path, filename)

        existing_size = 0
        if os.path.exists(local_file):
            existing_size = os.path.getsize(local_file)

        headers = {}
        if existing_size > 0:
            headers["Range"] = f"bytes={existing_size}-"

        response = requests.get(url, headers=headers, stream=True, timeout=(10, 60))

        if response.status_code == 416:
            response.close()
            return {
                "success": True,
                "message": f"文件已存在: {filename}",
                "file_path": local_file,
                "file_size": existing_size,
                "url": url,
            }

        if response.status_code not in (200, 206):
            response.close()
            return {
                "success": False,
                "error": f"Download failed with status code: {response.status_code}",
                "suggestion": "请尝试使用 curl 或 wget 命令作为替代方案下载此文件",
                "url": url,
            }

        is_resume = response.status_code == 206
        total_size = int(response.headers.get("content-length", 0))

        if is_resume:
            downloaded = existing_size
            total_size = existing_size + total_size
            mode = "ab"
        else:
            downloaded = 0
            mode = "wb"

        with open(local_file, mode) as f:
            for chunk in response.iter_content(chunk_size=8192):
                if is_stopped():
                    f.close()
                    response.close()
                    if os.path.exists(local_file):
                        os.remove(local_file)
                    return {
                        "success": False,
                        "error": "下载已取消",
                        "cancelled": True,
                        "url": url,
                    }
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

        response.close()

        final_size = os.path.getsize(local_file)

        if is_resume and final_size == existing_size:
            return {
                "success": True,
                "message": f"文件已存在（断点续传）: {filename}",
                "file_path": local_file,
                "file_size": final_size,
                "url": url,
                "resumed": True,
            }

        return {
            "success": True,
            "message": f"Successfully downloaded {filename}",
            "file_path": local_file,
            "file_size": final_size,
            "url": url,
            "resumed": is_resume,
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "下载超时",
            "suggestion": "请尝试使用 curl 或 wget 命令作为替代方案下载此文件",
            "url": url,
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Download failed: {str(e)}",
            "suggestion": "请尝试使用 curl 或 wget 命令作为替代方案下载此文件",
            "url": url,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "suggestion": "请尝试使用 curl 或 wget 命令作为替代方案下载此文件",
        }

import os
import requests
from pathlib import Path
from urllib.parse import urlparse


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

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(local_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)

        return {
            "success": True,
            "message": f"Successfully downloaded {filename}",
            "file_path": local_file,
            "file_size": downloaded,
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

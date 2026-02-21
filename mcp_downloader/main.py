import sys
import json
import os
from pathlib import Path

from mcp_downloader.tools.download_url import download_url
from mcp_downloader.tools.download_scp import download_scp
from mcp_downloader.tools.git_clone import git_clone
from mcp_downloader.utils import stop_flag
from mcp_downloader.utils.stop_flag import set_stop, reset


TOOLS = {
    "download_url": {
        "name": "download_url",
        "description": "Download files from HTTP/HTTPS URLs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to download from"},
                "path": {
                    "type": "string",
                    "description": "Local directory to save the file",
                    "default": "~/Downloads",
                },
            },
            "required": ["url"],
        },
    },
    "download_scp": {
        "name": "download_scp",
        "description": "Download files from remote servers via SCP (requires username and password)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Remote server IP or hostname",
                },
                "remote_path": {
                    "type": "string",
                    "description": "Path to the remote file",
                },
                "local_path": {
                    "type": "string",
                    "description": "Local directory to save the file",
                    "default": "~/Downloads",
                },
                "port": {"type": "integer", "description": "SSH port", "default": 22},
                "username": {"type": "string", "description": "SSH username"},
                "password": {"type": "string", "description": "SSH password"},
            },
            "required": ["host", "remote_path", "username", "password"],
        },
    },
    "git_clone": {
        "name": "git_clone",
        "description": "Clone Git repositories",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Git repository URL"},
                "path": {
                    "type": "string",
                    "description": "Local directory to clone into",
                    "default": ".",
                },
                "branch": {
                    "type": "string",
                    "description": "Branch to clone",
                    "default": None,
                },
            },
            "required": ["url"],
        },
    },
}


def handle_initialize():
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "mcp-downloader", "version": "0.1.0"},
        "tools": list(TOOLS.values()),
    }


def handle_tools_list():
    return {"tools": list(TOOLS.values())}


def handle_tool_call(tool_name, arguments):
    if tool_name == "download_url":
        return download_url(arguments.get("url"), arguments.get("path", "~/Downloads"))
    elif tool_name == "download_scp":
        return download_scp(
            host=arguments.get("host"),
            port=arguments.get("port", 22),
            username=arguments.get("username"),
            password=arguments.get("password"),
            remote_path=arguments.get("remote_path"),
            local_path=arguments.get("local_path", "~/Downloads"),
        )
    elif tool_name == "git_clone":
        return git_clone(
            url=arguments.get("url"),
            path=arguments.get("path", "."),
            branch=arguments.get("branch"),
        )
    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}


def process_request(request):
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        result = handle_initialize()
    elif method == "tools/list":
        result = handle_tools_list()
    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name")
        arguments = request.get("params", {}).get("arguments", {})
        result = handle_tool_call(tool_name, arguments)
    else:
        result = None

    response = {"jsonrpc": "2.0", "id": request_id}

    if result is not None:
        response["result"] = result
    else:
        response["error"] = {"code": -32601, "message": "Method not found"}

    return response


def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                set_stop()
                break

            request = json.loads(line.strip())

            if request.get("method") == "tools/call":
                reset()

            response = process_request(request)
            print(json.dumps(response), flush=True)

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()

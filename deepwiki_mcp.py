import json
import re
import time

import requests

MCP_URL = "https://mcp.deepwiki.com/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


class DeepWikiMCPError(Exception):
    pass


def repo_from_url(url):
    """'https://deepwiki.com/owner/repo' -> 'owner/repo'"""
    match = re.search(r"deepwiki\.com/([^/]+/[^/?#]+)", url)
    if not match:
        raise ValueError(f"Can't get owner/repo from {url}")
    return match.group(1)


def _parse_response(response):
    """The server answers with either plain JSON or an SSE stream of 'data:' lines."""
    if "text/event-stream" in response.headers.get("content-type", ""):
        for line in response.text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[len("data:"):].strip())
        raise DeepWikiMCPError(f"No data in SSE response: {response.text[:500]}")
    return response.json()


def ask_wiki_question(repo_name, question, timeout=300, retries=3):
    """Ask DeepWiki a question about a repo. Returns the answer text."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "ask_wiki_question",
            "arguments": {"repoName": repo_name, "question": question},
        },
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(MCP_URL, headers=HEADERS, json=payload, timeout=timeout)

            if response.status_code == 429 or response.status_code >= 500:
                wait = 30 * attempt
                print(f"[MCP] HTTP {response.status_code}, retrying in {wait}s ({attempt}/{retries})")
                time.sleep(wait)
                continue
            response.raise_for_status()

            data = _parse_response(response)
            if "error" in data:
                raise DeepWikiMCPError(f"MCP error: {data['error']}")

            result = data["result"]
            text = "".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
            if result.get("isError"):
                raise DeepWikiMCPError(f"Tool error: {text[:500]}")
            return text

        except requests.RequestException as e:
            if attempt == retries:
                raise DeepWikiMCPError(f"Request failed after {retries} attempts: {e}")
            wait = 30 * attempt
            print(f"[MCP] {e}, retrying in {wait}s ({attempt}/{retries})")
            time.sleep(wait)

    raise DeepWikiMCPError(f"Gave up after {retries} attempts")


def extract_search_url(answer):
    """DeepWiki appends 'View this search on DeepWiki: <url>' to answers."""
    match = re.search(r"https://deepwiki\.com/search/\S+", answer)
    return match.group(0) if match else None

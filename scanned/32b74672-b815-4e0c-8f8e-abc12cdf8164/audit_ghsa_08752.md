# [H] PraisonAI has an SSRF bypass

## Summary
Severity: High
Advisory: GHSA-q9pw-vmhh-384g
CVE: CVE-2026-44335
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-q9pw-vmhh-384g
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.32

## Details
### Summary
The URL checking logic in PraisonAI has a logical flaw that could be bypassed by attackers, leading to SSRF attacks.

### Details
The current PraisonAI project uses _validate_url to validate the input URL. The main logic is to perform security checks on the host portion of the URL extracted by urlparse to prevent SSRF attacks.

<img width="1290" height="1145" alt="QQ20260424-151256-24-1" src="https://github.com/user-attachments/assets/d5f16b74-5ad2-444f-8600-b05f78a4b769" />

However, there are indeed differences in parsing between urlparse and the library that actually sends the request. Currently, almost all application scenarios in this project involve first using _validate_url for URL validation, and then using _get_session().get to send the request.

<img width="1143" height="740" alt="QQ20260424-151437-24-2" src="https://github.com/user-attachments/assets/b1bf6ec2-d32a-4dac-b814-da819e8d3c83" />

In reality, its underlying mechanism is requests.get.

<img width="1042" height="576" alt="QQ20260424-151645-24-3" src="https://github.com/user-attachments/assets/e17352c3-4205-44d6-ab6e-75566480215b" />

The core issue: `urlparse()` and `requests` disagree on which host a URL like `http://127.0.0.1:6666\@1.1.1.1` points to:

- `urlparse()` treats `\` as a regular character and `@` as the userinfo-host delimiter, so it extracts hostname as `1.1.1.1` (public)
- `requests` treats `\` as a path character, connecting to `127.0.0.1` (internal)

Below is a test code I wrote following the code.

```
import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(r"D:/BaiduNetdiskDownload/PraisonAI-main/PraisonAI-main/src/praisonai-agents")))

from praisonaiagents.tools import spider_tools

# url = "http://127.0.0.1:6666\@1.1.1.1"
url = "http://127.0.0.1:6666"

result = spider_tools.scrape_page(url)

if isinstance(result, dict) and "error" in result:
    print("scrape failed:", result["error"])
else:
    pprint(result)
```
When an attacker uses `http://127.0.0.1:6666/`, the existing detection logic can detect that this is an internal network address and block it.

<img width="1068" height="128" alt="QQ20260424-152007-24-4" src="https://github.com/user-attachments/assets/294bff10-2af6-4960-bf69-dbf3340b1e9b" />

However, when an attacker uses `http://127.0.0.1:6666\@1.1.1.1`, the detection logic resolves the host to `1.1.1.1`, which is a public IP address, thus passing the verification. But in the actual request process, this URL is forwarded by requests.get to `http://127.0.0.1:6666`, bypassing the detection and achieving an SSRF attack.

<img width="2089" height="324" alt="QQ20260424-152123-24-5" src="https://github.com/user-attachments/assets/4421ce42-e47b-48de-a97a-56ce56a2bbc9" />

### PoC
```
http://127.0.0.1:6666\@1.1.1.1
```

### Impact
SSRF

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-q9pw-vmhh-384g
- https://nvd.nist.gov/vuln/detail/CVE-2026-44335
- https://github.com/MervinPraison/PraisonAI

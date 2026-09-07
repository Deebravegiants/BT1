# [H] Open WebUI has SSRF in /openai/models

## Summary
Severity: High
Advisory: GHSA-x757-hv69-jr45
CVE: CVE-2024-7959
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-x757-hv69-jr45
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
The `/openai/models` endpoint in open-webui/open-webui version 0.3.8 is vulnerable to Server-Side Request Forgery (SSRF). An attacker can change the OpenAI URL to any URL without checks, causing the endpoint to send a request to the specified URL and return the output. This vulnerability allows the attacker to access internal services and potentially gain command execution by accessing instance secrets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7959
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/3c8bea0a-d678-4d67-bb9c-2b5b610a2193

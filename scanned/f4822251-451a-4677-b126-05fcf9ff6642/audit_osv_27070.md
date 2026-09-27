# [M] Path Traversal and OS Command Injection in parisneo/lollms-webui

## Summary
Severity: Medium
Advisory: CVE-2024-10019
CVSS: 6.3 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10019
Type: osv

## Details
A vulnerability in the `start_app_server` function of parisneo/lollms-webui V12 (Strawberry) allows for path traversal and OS command injection. The function does not properly sanitize the `app_name` parameter, enabling an attacker to upload a malicious `server.py` file and execute arbitrary code by exploiting the path traversal vulnerability.

## References
- https://huntr.com/bounties/3cf80890-2d8a-4fc7-8e0e-6d4bf648b3ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10019.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10019

# [H] Absolute Path Traversal in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-6250
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-6250
Type: osv

## Details
An absolute path traversal vulnerability exists in parisneo/lollms-webui v9.6, specifically in the `open_file` endpoint of `lollms_advanced.py`. The `sanitize_path` function with `allow_absolute_path=True` allows an attacker to access arbitrary files and directories on a Windows system. This vulnerability can be exploited to read any file and list arbitrary directories on the affected system.

## References
- https://huntr.com/bounties/11a8bf9d-16f3-49b3-b5fc-ad36d8993c73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6250.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6250

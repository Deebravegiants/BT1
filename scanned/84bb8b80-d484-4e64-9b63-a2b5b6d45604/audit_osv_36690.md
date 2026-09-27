# [C] Remote Code Execution via Unrestricted File Upload in Bludit

## Summary
Severity: Critical
Advisory: CVE-2026-25099
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-25099
Type: osv

## Details
Bludit’s API plugin allows an authenticated attacker with a valid API token to upload files of any type and extension without restriction, which can then be executed, leading to Remote Code Execution.

This issue was fixed in 3.18.4.

## References
- https://github.com
- https://cert.pl/posts/2026/03/CVE-2026-25099
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25099.json
- https://github.com/bludit/bludit/releases/tag/3.18.4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25099
- https://github.com/bludit/bludit

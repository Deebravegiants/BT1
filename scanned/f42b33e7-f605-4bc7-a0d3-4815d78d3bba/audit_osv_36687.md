# [C] SunFounder Pironman Dashboard <= 1.3.13 Path Traversal Arbitrary File Read/Deletion

## Summary
Severity: Critical
Advisory: CVE-2026-25069
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-31
Source: https://osv.dev/vulnerability/CVE-2026-25069
Type: osv

## Details
SunFounder Pironman Dashboard (pm_dashboard) version 1.3.13 and prior contain a path traversal vulnerability in the log file API endpoints. An unauthenticated remote attacker can supply traversal sequences via the filename parameter to read and delete arbitrary files. Successful exploitation can disclose sensitive information and delete critical system files, resulting in data loss and potential system compromise or denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25069.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25069
- https://www.vulncheck.com/advisories/sunfounder-pironman-dashboard-path-traversal-arbitrary-file-read-deletion
- https://github.com/sunfounder/pm_dashboard/blob/main/pm_dashboard/pm_dashboard.py#L440
- https://github.com/sunfounder/pm_dashboard/blob/main/pm_dashboard/pm_dashboard.py#L62
- https://github.com/sunfounder/pm_dashboard
- https://gist.github.com/chapochapo/5db8702ede862af5c59a28b5d5a0aba3

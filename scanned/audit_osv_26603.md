# [M] Mattermost Desktop logs all keystrokes during initial run after fresh installation

## Summary
Severity: Medium
Advisory: CVE-2023-5339
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-10-17
Source: https://osv.dev/vulnerability/CVE-2023-5339
Type: osv

## Details
Mattermost Desktop fails to set an appropriate log level during initial run after fresh installation resulting in logging all keystrokes including password entry being logged.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5339.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5339

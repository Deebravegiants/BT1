# [H] CORS Misconfiguration in netease-youdao/qanything

## Summary
Severity: High
Advisory: CVE-2024-8024
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-8024
Type: osv

## Details
A CORS misconfiguration vulnerability exists in netease-youdao/qanything version 1.4.1. This vulnerability allows an attacker to bypass the Same-Origin Policy, potentially leading to sensitive information exposure. Properly implementing a restrictive CORS policy is crucial to prevent such security issues.

## References
- https://huntr.com/bounties/bda53fab-88aa-4e03-8d9d-4cf50a98ffc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8024.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8024

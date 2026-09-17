# [H] Worklenz Boolean-Based Blind SQL Injection via Improper ORDER BY Clause Input Validation

## Summary
Severity: High
Advisory: CVE-2026-25947
Aliases: CVE-2026-85388, GHSA-f2f8-2ppj-85pf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25947
Type: osv

## Details
Worklenz is a project management tool. Prior to 2.1.7, there are multiple SQL injection vulnerabilities were discovered in backend SQL query construction affecting project and task management controllers, reporting and financial data endpoints, real-time socket.io handlers, and resource allocation and scheduling features. The vulnerability has been patched in version v2.1.7.

## References
- https://github.com/Worklenz/worklenz/releases/tag/v2.1.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25947.json
- https://github.com/Worklenz/worklenz/security/advisories/GHSA-f2f8-2ppj-85pf
- https://nvd.nist.gov/vuln/detail/CVE-2026-25947
- https://github.com/Worklenz/worklenz/commit/76e5cb0f5dd566fb65586cd3db30ee951c92a32b

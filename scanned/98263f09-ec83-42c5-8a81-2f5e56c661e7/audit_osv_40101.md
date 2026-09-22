# [C] WebErpMesv2 has Unauthenticated RCE via Unrestricted File Upload in HR Expense scan_file (CWE-434)

## Summary
Severity: Critical
Advisory: CVE-2026-49827
Aliases: GHSA-chhq-7p67-2ff9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-49827
Type: osv

## Details
WebErpMesv2 is a Resource Management and Manufacturing execution system Web for industry. Versions 1.19 and prior allow any self-registered user to upload arbitrary PHP files through the HR Expense scan_file parameter, leading to Remote Code Execution. Combined with open registration (no invite required) and broken role middleware (CheckUserRole silently swallows RouteNotFoundException), this chain is effectively unauthenticated RCE against any default installation. The issue is patched in commit 5c54862fa044b363fd2be03d586750e81afd6818.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49827.json
- https://github.com/SMEWebify/WebErpMesv2/security/advisories/GHSA-chhq-7p67-2ff9
- https://nvd.nist.gov/vuln/detail/CVE-2026-49827
- https://github.com/SMEWebify/WebErpMesv2/commit/5c54862fa044b363fd2be03d586750e81afd6818

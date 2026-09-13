# [C] CI4MS Vulnerable to Remote Code Execution (RCE) via Arbitrary File Creation and Save in File Editor

## Summary
Severity: Critical
Advisory: CVE-2026-25510
Aliases: GHSA-gp56-f67f-m4px
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25510
Type: osv

## Details
CI4MS is a CodeIgniter 4-based CMS skeleton that delivers a production-ready, modular architecture with RBAC authorization and theme support. Prior to version 0.28.5.0, an authenticated user with file editor permissions can achieve Remote Code Execution (RCE) by leveraging the file creation and save endpoints, an attacker can upload and execute arbitrary PHP code on the server. This issue has been patched in version 0.28.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25510.json
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-gp56-f67f-m4px
- https://nvd.nist.gov/vuln/detail/CVE-2026-25510
- https://github.com/ci4-cms-erp/ci4ms/commit/86be2930d1c54eb7575102563302b2f3bafcb653

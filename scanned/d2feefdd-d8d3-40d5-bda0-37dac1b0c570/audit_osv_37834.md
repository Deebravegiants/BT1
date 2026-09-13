# [H] SiYuan has an Unauthenticated Arbitrary File Read via Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-33476
Aliases: GHSA-hhgj-gg9h-rjp7, GO-2026-4802
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33476
Type: osv

## Details
SiYuan is a personal knowledge management system. Prior to version 3.6.2, the Siyuan kernel exposes an unauthenticated file-serving endpoint under `/appearance/*filepath.` Due to improper path sanitization, attackers can perform directory traversal and read arbitrary files accessible to the server process. Authentication checks explicitly exclude this endpoint, allowing exploitation without valid credentials. Version 3.6.2 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33476.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-hhgj-gg9h-rjp7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33476
- https://github.com/siyuan-note/siyuan/commit/009bb598b3beccc972aa5f1ed88b3b224326bf2a

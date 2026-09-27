# [M] CouchAuth has a Server-Side Template Injection vulnerability in its email functionality

## Summary
Severity: Medium
Advisory: GHSA-r385-c5fc-x56c
CVE: CVE-2024-57177
CWE: CWE-1336, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-02-10
Source: https://github.com/advisories/GHSA-r385-c5fc-x56c
Type: github-advisory

## Affected
- npm: `@perfood/couch-auth` — affected >=0

## Details
A host header injection vulnerability exists in the NPM package of perfood/couch-auth <= 0.21.2. By sending a specially crafted host header in the email change confirmation request, it is possible to trigger a SSTI which can be leveraged to run limited commands or leak server-side information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57177
- https://github.com/perfood/couch-auth
- https://github.com/waristea/cve-research/tree/main/CVE-2024-57177

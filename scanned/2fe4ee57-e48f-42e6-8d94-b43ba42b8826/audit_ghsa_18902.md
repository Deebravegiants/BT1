# [M] @perfood/couch-auth may expose session tokens, passwords

## Summary
Severity: Medium
Advisory: GHSA-62vx-hpcr-m9ch
CVE: CVE-2025-60794
CWE: CWE-316
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-62vx-hpcr-m9ch
Type: github-advisory

## Affected
- npm: `@perfood/couch-auth` — affected >=0

## Details
Session tokens and passwords in couch-auth 0.21.2 are stored in JavaScript objects and remain in memory without explicit clearing in src/user.ts lines 700-707. This creates a window of opportunity for sensitive data extraction through memory dumps, debugging tools, or other memory access techniques, potentially leading to session hijacking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60794
- https://github.com/perfood/couch-auth
- https://github.com/pr0wl1ng/security-advisories/blob/main/CVE-2025-60794.md
- https://www.npmjs.com/package/@perfood/couch-auth

# [H] static-server Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-v834-rhv4-65m3
CVE: CVE-2023-26152
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-03
Source: https://github.com/advisories/GHSA-v834-rhv4-65m3
Type: github-advisory

## Affected
- npm: `static-server` — affected >=0

## Details
All versions of the package static-server are vulnerable to Directory Traversal due to improper input sanitization passed via the `validPath` function of server.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26152
- https://gist.github.com/lirantal/1f7021703a2065ecaf9ec9e06a3a346d
- https://github.com/nbluis/static-server
- https://github.com/nbluis/static-server/blob/master/server.js#L218-L223
- https://security.snyk.io/vuln/SNYK-JS-STATICSERVER-5722341

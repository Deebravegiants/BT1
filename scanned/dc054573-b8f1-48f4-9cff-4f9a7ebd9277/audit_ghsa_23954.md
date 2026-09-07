# [M] hexo-admin plugin for Node.js XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g784-q3p3-26rm
CVE: CVE-2019-17606
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g784-q3p3-26rm
Type: github-advisory

## Affected
- npm: `hexo-admin` — affected >=0

## Details
The Post editor functionality in the hexo-admin plugin versions 2.3.0 and earlier for Node.js is vulnerable to stored XSS via the content of a post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17606
- https://github.com/jaredly/hexo-admin/issues/185
- https://github.com/418sec/hexo-admin/pull/2
- https://github.com/jaredly/hexo-admin/pull/203
- https://github.com/jaredly/hexo-admin

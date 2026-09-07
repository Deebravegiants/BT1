# [M] Hexo Vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-q54r-r9pr-w7qv
CVE: CVE-2021-25987
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-q54r-r9pr-w7qv
Type: github-advisory

## Affected
- npm: `hexo` — affected >=0.0.1 <6.0.0

## Details
Hexo versions 0.0.1 to 5.4.0 are vulnerable against stored XSS. The post “body” and “tags” don’t sanitize malicious javascript during web page generation. Local unprivileged attacker can inject arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25987
- https://github.com/hexojs/hexo/issues/4838
- https://github.com/hexojs/hexo/pull/4750
- https://github.com/hexojs/hexo/commit/5170df2d3fa9c69e855c4b7c2b084ebfd92d5200
- https://github.com/hexojs/hexo
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25987

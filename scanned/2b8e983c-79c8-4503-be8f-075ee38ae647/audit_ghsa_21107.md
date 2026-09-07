# [M] markdown-it-decorate vulnerable to cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-rhf5-2378-3w3w
CVE: CVE-2020-28459
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-19
Source: https://github.com/advisories/GHSA-rhf5-2378-3w3w
Type: github-advisory

## Affected
- npm: `markdown-it-decorate` — affected >=0

## Details
markdown-it-decorate adds attributes, IDs and classes to Markdown, and the most recent version 1.2.2 was published in 2017. All versions are currently vulnerable to cross-site scripting (XSS) and there is no fixed version at this time

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28459
- https://github.com/rstacruz/markdown-it-decorate/commit/a6b33ce79e9b8cddf6184c754713e6af65253909
- https://github.com/rstacruz/markdown-it-decorate
- https://security.snyk.io/vuln/SNYK-JS-MARKDOWNITDECORATE-1044068

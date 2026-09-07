# [M] Cross-site Scripting in PrimeFaces

## Summary
Severity: Medium
Advisory: GHSA-fw5f-7c6c-3vmv
CVE: CVE-2020-10544
CWE: CWE-79
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-fw5f-7c6c-3vmv
Type: github-advisory

## Affected
- npm: `primefaces` — affected >=0 <8.0
- Maven: `org.primefaces:primefaces` — affected >=0 <8.0

## Details
An XSS issue was discovered in tooltip/tooltip.js in PrimeTek PrimeFaces 7.0.11. In a web application using PrimeFaces, an attacker can provide JavaScript code in an input field whose data is later used as a tooltip title without any input validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10544
- https://github.com/primefaces/primefaces/issues/5642
- https://github.com/primefaces/primefaces/commit/9982c4f7a83f75e3ab06168fa283e3d6128dfd1f
- https://github.com/primefaces/primefaces

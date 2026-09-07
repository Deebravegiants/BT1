# [M] iziModal Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h685-83w4-3ph3
CVE: CVE-2021-32860
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-h685-83w4-3ph3
Type: github-advisory

## Affected
- npm: `izimodal` — affected >=0 <1.6.1

## Details
iziModal is a modal plugin with jQuery. Versions prior to 1.6.1 are vulnerable to cross-site scripting (XSS) when handling untrusted modal titles. An attacker who is able to influence the field `title` when creating a `iziModal` instance is able to supply arbitrary `html` or `javascript` code that will be rendered in the context of a user, potentially leading to `XSS`. Version 1.6.1 contains a patch for this issue

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32860
- https://github.com/marcelodolza/iziModal/issues/249
- https://github.com/marcelodolza/iziModal/commit/01728ac52bac5c1b4512087dafe0ad8b091fdc9e
- https://github.com/marcelodolza/iziModal
- https://securitylab.github.com/advisories/GHSL-2021-1044_iziModal

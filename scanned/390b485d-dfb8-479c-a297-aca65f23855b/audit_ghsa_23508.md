# [M] Joomla! XSS in Default Templates

## Summary
Severity: Medium
Advisory: GHSA-v84j-vh7x-g7j6
CVE: CVE-2019-16725
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v84j-vh7x-g7j6
Type: github-advisory

## Affected
- Packagist: `joomla/joomla-cms` — affected >=3.0.0 <3.9.12

## Details
In Joomla! 3.x before 3.9.12, inadequate escaping allowed XSS attacks using the logo parameter of the default templates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16725
- https://developer.joomla.org/security-centre/791-20190901-core-xss-in-logo-parameter-of-default-templates.html
- https://github.com/joomla/joomla-cms

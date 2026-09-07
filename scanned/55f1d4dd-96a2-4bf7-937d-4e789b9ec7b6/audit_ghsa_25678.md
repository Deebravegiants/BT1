# [M] Cross site scripting in valine

## Summary
Severity: Medium
Advisory: GHSA-6xvq-2gj8-4276
CVE: CVE-2020-28847
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-6xvq-2gj8-4276
Type: github-advisory

## Affected
- npm: `valine` — affected >=0 <1.4.15

## Details
valine is a fast, simple & powerful comment system. Cross Site Scripting (XSS) vulnerability in xCss Valine v1.4.14 via the nick parameter to /classes/Comment. A fix was released in version 1.4.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28847
- https://github.com/xCss/Valine/issues/348
- https://github.com/xCss/Valine
- https://github.com/xCss/Valine/releases/tag/v1.4.15

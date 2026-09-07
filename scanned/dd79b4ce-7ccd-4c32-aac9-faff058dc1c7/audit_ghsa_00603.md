# [M] Cross-Site Scripting in sanitize-html

## Summary
Severity: Medium
Advisory: GHSA-wg96-3933-j2w5
CVE: CVE-2017-16017
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-wg96-3933-j2w5
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=0 <1.2.3

## Details
Affected versions of `sanitize-html` are vulnerable to cross-site scripting.

## Proof of Concept:

`<IMG SRC= onmouseover="alert('XSS');">`
produces the following:

`<img src="onmouseover="alert('XSS');"" />`
This is definitely invalid HTML, but would suggest that it's being interpreted incorrectly by the parser.


## Recommendation

Update to version 1.2.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16017
- https://github.com/punkave/sanitize-html/issues/19
- https://github.com/punkave/sanitize-html/pull/20
- https://github.com/advisories/GHSA-wg96-3933-j2w5
- https://www.npmjs.com/advisories/155

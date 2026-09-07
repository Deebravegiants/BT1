# [H] Cross-Site Scripting in bracket-template

## Summary
Severity: High
Advisory: GHSA-jj6g-7j8p-7gf2
CWE: CWE-79
Ecosystem: npm
Published: 2019-05-30
Source: https://github.com/advisories/GHSA-jj6g-7j8p-7gf2
Type: github-advisory

## Affected
- npm: `bracket-template` — affected >=0

## Details
All versions of `bracket-template` are vulnerable to stored cross-site scripting (XSS). This is exploitable when a variable passed in via a GET parameter is used in a template.


## Recommendation

No fix is currently available for this vulnerability. It is our recommendation to not install or use this module at this time.

## References
- https://hackerone.com/reports/317125
- https://www.npmjs.com/advisories/608

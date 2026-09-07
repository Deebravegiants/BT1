# [H] Cross-Site Scripting in serve

## Summary
Severity: High
Advisory: GHSA-xw79-hhv6-578c
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-xw79-hhv6-578c
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <10.0.2

## Details
Versions of `serve` prior to 10.0.2 are vulnerable to Cross-Site Scripting (XSS). The package does not encode output, allowing attackers to execute arbitrary JavaScript in the victim's browser if user-supplied input is rendered.


## Recommendation

Upgrade to version 10.0.2 or later.

## References
- https://github.com/zeit/serve-handler/commit/65b4d4183a31a8076c78c40118acb0ca1b64f620
- https://hackerone.com/reports/358641
- https://hackerone.com/reports/398285
- https://github.com/zeit/serve-handler
- https://www.npmjs.com/advisories/971

# [H] Cross-Site Scripting in console-feed

## Summary
Severity: High
Advisory: GHSA-g9wg-wq4f-2x5w
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-g9wg-wq4f-2x5w
Type: github-advisory

## Affected
- npm: `console-feed` — affected >=0 <2.8.10

## Details
Versions of `console-feed` prior to 2.8.10 are vulnerable to Cross-Site Scripting (XSS). The package fails to properly escape the rendered output. If an application uses `console-feed` and a malicious JavaScript payload was passed to a `console.log('%_', payload)` call, the package would render HTML containing the malicious payload.


## Recommendation

Upgrade to version 2.8.10 or later.

## References
- https://www.npmjs.com/advisories/1088

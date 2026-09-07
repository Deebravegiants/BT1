# [H] Cross-Site Scripting in cmmn-js-properties-panel

## Summary
Severity: High
Advisory: GHSA-vmh4-322v-cfpc
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-vmh4-322v-cfpc
Type: github-advisory

## Affected
- npm: `cmmn-js-properties-panel` — affected >=0 <0.8.0

## Details
Versions of `cmmn-js-properties-panel` prior to 0.8.0 are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize input in specially configured diagrams, which may allow attackers to inject arbitrary JavaScript in the embedding website.


## Recommendation

Upgrade to version 0.8.0 or later.

## References
- https://www.npmjs.com/advisories/1080

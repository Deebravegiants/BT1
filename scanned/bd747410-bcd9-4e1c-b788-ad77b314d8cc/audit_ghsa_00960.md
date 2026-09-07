# [H] Cross-Site Scripting in dmn-js-properties-panel

## Summary
Severity: High
Advisory: GHSA-h9wr-xr4r-66fh
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-h9wr-xr4r-66fh
Type: github-advisory

## Affected
- npm: `dmn-js-properties-panel` — affected >=0 <0.3.0

## Details
Versions of `dmn-js-properties-panel` prior to 0.8.0 are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize input in specially configured diagrams, which may allow attackers to inject arbitrary JavaScript in the embedding website.


## Recommendation

Upgrade to version 0.3.0 or later.

## References
- https://www.npmjs.com/advisories/1081

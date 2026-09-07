# [H] Cross-Site Scripting in bpmn-js-properties-panel

## Summary
Severity: High
Advisory: GHSA-vpj4-89q8-rh38
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-vpj4-89q8-rh38
Type: github-advisory

## Affected
- npm: `bpmn-js-properties-panel` — affected >=0 <0.31.0

## Details
Versions of `bpmn-js-properties-panel` prior to 0.31.0 are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize input in specially configured diagrams, which may allow attackers to inject arbitrary JavaScript in the embedding website.


## Recommendation

Upgrade to version 0.31.0 or later.

## References
- https://www.npmjs.com/advisories/1079

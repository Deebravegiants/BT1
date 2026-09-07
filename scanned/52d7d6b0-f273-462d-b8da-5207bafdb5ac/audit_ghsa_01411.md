# [H] Cross-Site Scripting in fomantic-ui

## Summary
Severity: High
Advisory: GHSA-788m-pj96-7w2c
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-788m-pj96-7w2c
Type: github-advisory

## Affected
- npm: `fomantic-ui` — affected >=0 <2.7.0

## Details
Versions of `fomantic-ui` are vulnerable to Cross-Site Scripting. Lack of output encoding on the selection dropdowns can lead to user input being executed instead of printed as text.


## Recommendation

Upgrade to version 2.7.0 or later.

## References
- https://github.com/fomantic/Fomantic-UI
- https://github.com/fomantic/Fomantic-UI/releases/tag/2.7.0
- https://www.npmjs.com/advisories/885

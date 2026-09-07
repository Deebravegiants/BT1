# [M] Cross-Site Scripting in bootbox

## Summary
Severity: Medium
Advisory: GHSA-87mg-h5r3-hw88
CWE: CWE-64, CWE-79
Ecosystem: npm
Published: 2019-05-30
Source: https://github.com/advisories/GHSA-87mg-h5r3-hw88
Type: github-advisory

## Affected
- npm: `bootbox` — affected >=0

## Details
All version of `bootbox` are vulnerable to Cross-Site Scripting. The package does not sanitize user input in the provided dialog boxes, allowing attackers to inject HTML code and execute arbitrary JavaScript.


## Recommendation

Sanitize user input being passed to `bootbox` or consider using an alternative package.

## References
- https://github.com/makeusabrew/bootbox/issues/661
- https://hackerone.com/reports/508446
- https://github.com/makeusabrew/bootbox
- https://www.npmjs.com/advisories/882

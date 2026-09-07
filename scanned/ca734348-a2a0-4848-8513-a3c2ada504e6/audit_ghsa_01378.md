# [H] Cross-Site Scripting in markdown-it-katex

## Summary
Severity: High
Advisory: GHSA-5ff8-jcf9-fw62
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-5ff8-jcf9-fw62
Type: github-advisory

## Affected
- npm: `markdown-it-katex` — affected >=0.0.0

## Details
All versions of `markdown-it-katex` are vulnerable to Cross-Site Scripting (XSS). The package fails to properly escape error messages, which may allow attackers to execute arbitrary JavaScript in a victim's browser by triggering an error.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/waylonflinn/markdown-it-katex/issues/26
- https://github.com/waylonflinn/markdown-it-katex
- https://www.npmjs.com/advisories/1466

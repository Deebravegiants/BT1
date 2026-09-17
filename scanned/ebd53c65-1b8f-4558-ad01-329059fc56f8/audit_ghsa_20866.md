# [H] d3-color vulnerable to ReDoS

## Summary
Severity: High
Advisory: GHSA-36jr-mh4h-2g58
CWE: CWE-1333, CWE-400
Ecosystem: npm
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-36jr-mh4h-2g58
Type: github-advisory

## Affected
- npm: `d3-color` — affected >=1.0.2 <3.1.0

## Details
The d3-color module provides representations for various color spaces in the browser. Versions prior to 3.1.0 are vulnerable to a Regular expression Denial of Service. This issue has been patched in version 3.1.0. There are no known workarounds.

## References
- https://github.com/d3/d3-color/pull/100
- https://github.com/d3/d3-color
- https://github.com/d3/d3-color/releases/tag/v3.1.0
- https://security.snyk.io/vuln/SNYK-JS-D3COLOR-1076592

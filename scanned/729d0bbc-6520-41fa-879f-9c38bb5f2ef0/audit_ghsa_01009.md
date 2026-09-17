# [H] Remote Code Execution in office-converter

## Summary
Severity: High
Advisory: GHSA-9p64-h5q4-phpm
CWE: CWE-20
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-9p64-h5q4-phpm
Type: github-advisory

## Affected
- npm: `office-converter` — affected >=0.0.0

## Details
All versions of `office-converter` are vulnerable to Remote Code Execution. Due to insufficient input validation an attacker could run arbitrary commands on the server thus rendering the package vulnerable to Remote Code Execution.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/759

# [H] Command Injection in fs-path

## Summary
Severity: High
Advisory: GHSA-gc94-6w89-hpqr
CWE: CWE-77
Ecosystem: npm
Published: 2019-06-12
Source: https://github.com/advisories/GHSA-gc94-6w89-hpqr
Type: github-advisory

## Affected
- npm: `fs-path` — affected >=0 <0.0.25

## Details
All versions of `fs-path` are vulnerable to command injection is unsanitized user input is passed in.


## Recommendation

No fix is currently available for this vulnerability. It is our recommendation to not install or use this module until a fix is available.

## References
- https://github.com/pillys/fs-path/pull/5
- https://hackerone.com/reports/324491
- https://github.com/pillys/fs-path
- https://www.npmjs.com/advisories/661

# [H] Remote Code Execution in pomelo-monitor

## Summary
Severity: High
Advisory: GHSA-m5ch-gx8g-rg73
CWE: CWE-20
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-m5ch-gx8g-rg73
Type: github-advisory

## Affected
- npm: `pomelo-monitor` — affected >=0.0.0

## Details
All versions of `pomelo-monitor` are vulnerable to Remote Code Execution. Due to insufficient input validation an attacker could run arbitrary commands on the server thus rendering the package vulnerable to Remote Code Execution.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/756

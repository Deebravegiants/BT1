# [H] Command Injection in cocos-utils

## Summary
Severity: High
Advisory: GHSA-rffp-mc78-wjf7
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-rffp-mc78-wjf7
Type: github-advisory

## Affected
- npm: `cocos-utils` — affected >=0

## Details
All versions of `cocos-utils` are vulnerable to Remote Code Execution. The `unzip()` function concatenates user input to `exec()` which may allow attackers to execute arbitrary commands  on the server.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/829

# [H] Command Injection in expressfs

## Summary
Severity: High
Advisory: GHSA-mxmj-84q8-34r7
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-mxmj-84q8-34r7
Type: github-advisory

## Affected
- npm: `expressfs` — affected >=0

## Details
All versions of `expressfs` are vulnerable to Command Injection. The package does not validate user input on several API endpoints, allowing attackers to run arbitrary commands in the system. The affected endpoints are: `expressfs.appendFile`,  `expressfs.cp`, `expressfs.create` and `expressfs.rmdir`.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/953

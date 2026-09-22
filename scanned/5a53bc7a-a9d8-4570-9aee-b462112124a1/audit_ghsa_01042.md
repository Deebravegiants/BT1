# [H] Command Injection in treekill

## Summary
Severity: High
Advisory: GHSA-533p-g2hq-qr26
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-533p-g2hq-qr26
Type: github-advisory

## Affected
- npm: `treekill` — affected >=0.0.0

## Details
All versions of `treekill` are vulnerable to Command Injection. The package fails to sanitize values passed to the  `kill` function. If this value is user-controlled it  may allow attackers to run arbitrary commands in the server. The issue only affects Windows systems.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://hackerone.com/reports/703415
- https://www.npmjs.com/advisories/1433

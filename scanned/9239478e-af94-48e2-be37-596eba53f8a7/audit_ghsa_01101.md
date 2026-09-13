# [C] Command Injection in node-wifi

## Summary
Severity: Critical
Advisory: GHSA-4x6x-782q-jfc4
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-4x6x-782q-jfc4
Type: github-advisory

## Affected
- npm: `node-wifi` — affected >=0 <2.0.12

## Details
Versions of `node-wifi` prior to 2.0.12 are vulnerable to Command Injection. The package fails to sanitize user input, allowing attackers to inject commands through the `ssid` variable and possibly achieving Remote Code Execution on the system.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/952

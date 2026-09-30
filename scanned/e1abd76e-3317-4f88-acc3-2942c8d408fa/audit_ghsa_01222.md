# [C] Command Injection in traceroute

## Summary
Severity: Critical
Advisory: GHSA-rjvj-673q-4hfw
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-rjvj-673q-4hfw
Type: github-advisory

## Affected
- npm: `traceroute` — affected >=0.0.0

## Details
All versions of `traceroute` are vulnerable to Command Injection. The package fails to sanitize input and passes it directly to an `exec` call, which may allow attackers to execute arbitrary code in the system. The `trace` function is vulnerable and can be abused if the `host` value is controlled by an attacker.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/jaw187/node-traceroute
- https://snyk.io/vuln/npm:traceroute:20160311
- https://www.npmjs.com/advisories/1465

# [M] Command Injection in wizard-syncronizer

## Summary
Severity: Medium
Advisory: GHSA-wgw3-gf4p-62xc
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-wgw3-gf4p-62xc
Type: github-advisory

## Affected
- npm: `wizard-syncronizer` — affected >=0.0.0

## Details
All versions of `wizard-syncronizer` are vulnerable to Command Injection. The package does not validate input on the `cloneAndSync` function  and concatenates it to an exec call. This can be abused through a malicious widget containing the payload in the `gitURL` value or through a MITM attack since the package does not enforce HTTPS. This may allow attackers to run arbitrary commands in the system.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://www.npmjs.com/advisories/977

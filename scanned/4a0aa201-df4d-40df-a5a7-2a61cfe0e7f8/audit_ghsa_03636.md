# [M] Command Injection in dot

## Summary
Severity: Medium
Advisory: GHSA-4859-gpc7-4j66
CWE: CWE-77
Ecosystem: npm
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-4859-gpc7-4j66
Type: github-advisory

## Affected
- npm: `dot` — affected >=0

## Details
All versions of dot are vulnerable to Command Injection. The template compilation may execute arbitrary commands if an attacker can inject code in the template or if a Prototype Pollution-like vulnerability can be exploited to alter an Object's prototype.

## References
- https://hackerone.com/reports/390929
- https://www.npmjs.com/advisories/798

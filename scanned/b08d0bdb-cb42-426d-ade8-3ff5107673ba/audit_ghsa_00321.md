# [H] ikst Downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-w23f-f3c5-r9qh
CVE: CVE-2017-16041
CWE: CWE-311
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-w23f-f3c5-r9qh
Type: github-advisory

## Affected
- npm: `ikst` — affected >=0 <1.1.2

## Details
Affected versions of `ikst` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. While the exact severity of impact for a vulnerability like this is highly variable and depends on the behavior of the package itself, it ranges from being able to read sensitive information all the way up to and including remote code execution.


## Recommendation

Upgrade to version 1.1.2 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16041
- https://github.com/advisories/GHSA-w23f-f3c5-r9qh
- https://www.npmjs.com/advisories/249

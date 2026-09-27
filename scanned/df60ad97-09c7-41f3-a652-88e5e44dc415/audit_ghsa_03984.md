# [H] Downloads Resources over HTTP in kindlegen

## Summary
Severity: High
Advisory: GHSA-h7pc-85cg-wmch
CVE: CVE-2016-10575
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-h7pc-85cg-wmch
Type: github-advisory

## Affected
- npm: `kindlegen` — affected >=0 <1.1.0

## Details
Affected versions of `kindlegen` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `kindlegen`.


## Recommendation

Update to version 1.1.0 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10575
- https://github.com/advisories/GHSA-h7pc-85cg-wmch
- https://www.npmjs.com/advisories/251

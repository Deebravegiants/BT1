# [H] nodeschnaps downloads resources over HTTP

## Summary
Severity: High
Advisory: GHSA-r74q-wqx8-2pr3
CVE: CVE-2016-10622
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-r74q-wqx8-2pr3
Type: github-advisory

## Affected
- npm: `nodeschnaps` — affected >=0 <1.0.3

## Details
Affected versions of `nodeschnaps` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `nodeschnaps`.


## Recommendation

Update to version 1.0.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10622
- https://github.com/advisories/GHSA-r74q-wqx8-2pr3
- https://www.npmjs.com/advisories/212

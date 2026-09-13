# [H] Downloads Resources over HTTP in alto-saxophone

## Summary
Severity: High
Advisory: GHSA-2p69-gxpm-5469
CVE: CVE-2016-10694
CWE: CWE-311
Ecosystem: npm
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-2p69-gxpm-5469
Type: github-advisory

## Affected
- npm: `alto-saxophone` — affected >=0 <2.25.1

## Details
Affected versions of `alto-saxophone` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `alto-saxophone`.


## Recommendation

Update to version 2.25.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10694
- https://github.com/advisories/GHSA-2p69-gxpm-5469
- https://www.npmjs.com/advisories/172

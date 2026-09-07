# [H] Downloads Resources over HTTP in baryton-saxophone

## Summary
Severity: High
Advisory: GHSA-6pwf-whc8-hjf6
CVE: CVE-2016-10573
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-6pwf-whc8-hjf6
Type: github-advisory

## Affected
- npm: `baryton-saxophone` — affected >=0 <3.0.1

## Details
Affected versions of `baryton-saxophone` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `baryton-saxophone`.


## Recommendation

Update to version 3.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10573
- https://github.com/advisories/GHSA-6pwf-whc8-hjf6
- https://www.npmjs.com/advisories/240

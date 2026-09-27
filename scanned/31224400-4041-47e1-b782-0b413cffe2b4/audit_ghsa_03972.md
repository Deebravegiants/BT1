# [H] Downloads Resources over HTTP in prince

## Summary
Severity: High
Advisory: GHSA-cr79-9pwf-r6f5
CVE: CVE-2016-10591
CWE: CWE-269, CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-cr79-9pwf-r6f5
Type: github-advisory

## Affected
- npm: `prince` — affected >=0 <1.4.7

## Details
Affected versions of `prince` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `prince`.


## Recommendation

Update to version 1.4.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10591
- https://github.com/advisories/GHSA-cr79-9pwf-r6f5
- https://github.com/rse/node-prince
- https://www.npmjs.com/advisories/185

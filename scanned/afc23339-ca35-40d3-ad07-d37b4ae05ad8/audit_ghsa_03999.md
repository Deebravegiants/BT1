# [H] Downloads Resources over HTTP in limbus-buildgen

## Summary
Severity: High
Advisory: GHSA-rj38-87f3-93p6
CVE: CVE-2016-10674
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-rj38-87f3-93p6
Type: github-advisory

## Affected
- npm: `limbus-buildgen` — affected >=0 <0.1.1

## Details
Affected versions of `limbus-buildgen` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `limbus-buildgen`.


## Recommendation

Update to version 0.1.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10674
- https://github.com/advisories/GHSA-rj38-87f3-93p6
- https://www.npmjs.com/advisories/276

# [H] Downloads Resources over HTTP in mongodb-instance

## Summary
Severity: High
Advisory: GHSA-7r8m-45gc-m2c8
CVE: CVE-2016-10572
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-7r8m-45gc-m2c8
Type: github-advisory

## Affected
- npm: `mongodb-instance` — affected >=0 <0.0.3

## Details
Affected versions of `mongodb-instance` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `mongodb-instance`.


## Recommendation

Update to version 0.0.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10572
- https://github.com/Janpot/mongodb-instance/commit/c8fea750f8020ace8410c442b2684b33a9fddd3b)
- https://github.com/advisories/GHSA-7r8m-45gc-m2c8
- https://www.npmjs.com/advisories/235

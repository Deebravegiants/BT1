# [H] Downloads Resources over HTTP in product-monitor

## Summary
Severity: High
Advisory: GHSA-h2r4-4xgf-3865
CVE: CVE-2016-10567
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-h2r4-4xgf-3865
Type: github-advisory

## Affected
- npm: `product-monitor` — affected >=0 <2.2.5

## Details
Affected versions of `product-monitor` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `product-monitor`.


## Recommendation

Update to versions 2.2.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10567
- https://github.com/advisories/GHSA-h2r4-4xgf-3865
- https://www.npmjs.com/advisories/171

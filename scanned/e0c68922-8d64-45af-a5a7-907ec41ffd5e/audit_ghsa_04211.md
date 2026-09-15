# [M] ts-deepmerge: Prototype Method Override leads to DoS

## Summary
Severity: Medium
Advisory: GHSA-87mf-gv2c-c62c
CVE: CVE-2026-12644
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-87mf-gv2c-c62c
Type: github-advisory

## Affected
- npm: `ts-deepmerge` — affected >=0 <8.0.0

## Details
Versions of the package ts-deepmerge before 8.0.0 are vulnerable to Uncaught Exception due to the improper handling of built-in Object.prototype methods (such as toString, valueOf). When user-controlled input contains these keys with non-function values, the resulting merged object becomes broken — any string context operation throws a TypeError, crashing the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12644
- https://github.com/voodoocreation/ts-deepmerge/commit/305a05831a462fb2c353d3cbbff55a0733286f8c
- https://gist.github.com/igorg1312/775fa00114c4d47df6ae0551779ab407
- https://github.com/voodoocreation/ts-deepmerge
- https://security.snyk.io/vuln/SNYK-JS-TSDEEPMERGE-17339141

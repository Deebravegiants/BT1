# [M] Prototype Pollution in extend

## Summary
Severity: Medium
Advisory: GHSA-qrmc-fj45-qfc2
CVE: CVE-2018-16492
CWE: CWE-400
Ecosystem: npm
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-qrmc-fj45-qfc2
Type: github-advisory

## Affected
- npm: `extend` — affected >=3.0.0 <3.0.2
- npm: `extend` — affected >=1.1.3 <2.0.2

## Details
Versions of `extend` prior to 3.0.2 (for 3.x) and 2.0.2 (for 2.x) are vulnerable to Prototype Pollution. The `extend()` function allows attackers to modify the prototype of Object causing the addition or modification of an existing property that will exist on all objects.




## Recommendation

If you're using `extend` 3.x upgrade to 3.0.2 or later.
If you're using `extend` 2.x upgrade to 2.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16492
- https://github.com/github/advisory-database/pull/6695
- https://github.com/justmoon/node-extend/pull/48
- https://github.com/justmoon/node-extend/commit/0e68e71d93507fcc391e398bc84abd0666b28190
- https://hackerone.com/reports/381185
- https://github.com/justmoon/node-extend

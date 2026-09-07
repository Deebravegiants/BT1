# [C] Prototype Pollution in deep-extend

## Summary
Severity: Critical
Advisory: GHSA-hr2v-3952-633q
CVE: CVE-2018-3750
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-hr2v-3952-633q
Type: github-advisory

## Affected
- npm: `deep-extend` — affected >=0 <0.5.1

## Details
Versions of `deep-extend` before 0.5.1 are vulnerable to prototype pollution.


## Recommendation

Update to version 0.5.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3750
- https://github.com/unclechu/node-deep-extend/commit/9423fae877e2ab6b4aecc4db79a0ed63039d4703
- https://hackerone.com/reports/311333
- https://github.com/advisories/GHSA-hr2v-3952-633q
- https://www.npmjs.com/advisories/612

# [M] Signatures are mistakenly recognized to be valid in jsrsasign

## Summary
Severity: Medium
Advisory: GHSA-h87q-g2wp-47pj
CWE: CWE-347
Ecosystem: npm
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-h87q-g2wp-47pj
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <10.2.0

## Details
In the jsrsasign package through 10.1.13 for Node.js, some invalid RSA PKCS#1 v1.5 signatures are mistakenly recognized to be valid. NOTE: there is no known practical attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30246
- https://github.com/kjur/jsrsasign/issues/478
- https://github.com/kjur/jsrsasign/releases/tag/10.1.13
- https://github.com/kjur/jsrsasign/releases/tag/10.2.0
- https://kjur.github.io/jsrsasign

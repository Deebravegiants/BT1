# [H] Prototype Pollution in extend2

## Summary
Severity: High
Advisory: GHSA-gjm5-83cw-p3p2
CVE: CVE-2021-23568
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-gjm5-83cw-p3p2
Type: github-advisory

## Affected
- npm: `extend2` — affected >=0 <1.0.1

## Details
The package extend2 before 1.0.1 are vulnerable to Prototype Pollution via the extend function due to unsafe recursive merge.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23568
- https://github.com/eggjs/extend2/pull/2
- https://github.com/eggjs/extend2/commit/aa332a59116c8398976434b57ea477c6823054f8
- https://github.com/eggjs/extend2
- https://github.com/eggjs/extend2/blob/master/index.js%23L50-L60
- https://snyk.io/vuln/SNYK-JS-EXTEND2-2320315

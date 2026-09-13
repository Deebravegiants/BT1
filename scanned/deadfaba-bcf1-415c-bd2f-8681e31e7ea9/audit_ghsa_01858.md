# [H] Prototype Pollution in ts-nodash

## Summary
Severity: High
Advisory: GHSA-5xjx-4xcm-hpcm
CVE: CVE-2021-23403
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-5xjx-4xcm-hpcm
Type: github-advisory

## Affected
- npm: `ts-nodash` — affected >=0 <1.2.7

## Details
`ts-nodash` before version 1.2.7 is vulnerable to Prototype Pollution via the Merge() function due to lack of validation input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23403
- https://github.com/BadOPCode/NoDash/commit/b9cc2b3b49f6cd5228e406bc57e17a28b998fea5
- https://github.com/BadOPCode/NoDash
- https://github.com/BadOPCode/NoDash/blob/master/src/Merge.ts
- https://snyk.io/vuln/SNYK-JS-TSNODASH-1311009

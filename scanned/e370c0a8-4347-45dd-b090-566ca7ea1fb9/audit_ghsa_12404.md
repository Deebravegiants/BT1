# [M] Directory Traversal in evershop

## Summary
Severity: Medium
Advisory: GHSA-7443-5962-wp4r
CVE: CVE-2023-46497
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-7443-5962-wp4r
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.8

## Details
Directory Traversal vulnerability in EverShop NPM versions before v.1.0.0-rc.8 allows a remote attacker to obtain sensitive information via a crafted request to the mkdirSync function in the folderCreate/createFolder.js endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46497
- https://github.com/evershopcommerce/evershop/pull/338
- https://devhub.checkmarx.com/cve-details/CVE-2023-46497
- https://devhub.checkmarx.com/cve-details/Cx16846793-56b6
- https://github.com/evershopcommerce/evershop

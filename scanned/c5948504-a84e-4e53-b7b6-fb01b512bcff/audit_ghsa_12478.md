# [M] Directory Traversal in evershop

## Summary
Severity: Medium
Advisory: GHSA-4wrm-qmq2-5fjx
CVE: CVE-2023-46493
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-4wrm-qmq2-5fjx
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.8

## Details
Directory Traversal vulnerability in EverShop NPM versions before v.1.0.0-rc.8 allows a remote attacker to obtain sensitive information via a crafted request to the readDirSync function in fileBrowser/browser.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46493
- https://github.com/evershopcommerce/evershop/pull/338
- https://devhub.checkmarx.com/cve-details/CVE-2023-46493
- https://devhub.checkmarx.com/cve-details/Cxa4d94170-be41
- https://github.com/evershopcommerce/evershop

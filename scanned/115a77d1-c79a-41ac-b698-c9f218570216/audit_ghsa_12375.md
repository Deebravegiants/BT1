# [M] Cross Site Scripting in evershop

## Summary
Severity: Medium
Advisory: GHSA-m6vm-ff9v-jp3r
CVE: CVE-2023-46494
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-m6vm-ff9v-jp3r
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.5

## Details
Cross Site Scripting vulnerability in EverShop NPM versions before v.1.0.0-rc.5 allows a remote attacker to obtain sensitive information via a crafted request to the ProductGrid function in admin/productGrid/Grid.jsx.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46494
- https://github.com/evershopcommerce/evershop/pull/244
- https://devhub.checkmarx.com/cve-details/CVE-2023-46494
- https://devhub.checkmarx.com/cve-details/Cx8ecec391-2014
- https://github.com/evershopcommerce/evershop

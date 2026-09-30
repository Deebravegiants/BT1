# [C] Code execution in evershop

## Summary
Severity: Critical
Advisory: GHSA-5mmr-9qx3-3pf9
CVE: CVE-2023-46498
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-08
Source: https://github.com/advisories/GHSA-5mmr-9qx3-3pf9
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0 <1.0.0-rc.8

## Details
An issue in EverShop NPM versions before v.1.0.0-rc.8 allows a remote attacker to obtain sensitive information and execute arbitrary code via the /deleteCustomer/route.json file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46498
- https://github.com/evershopcommerce/evershop/pull/342
- https://devhub.checkmarx.com/cve-details/Cx8b24ace3-0c9a
- https://devhub.checkmarx.com/cve-details/cve-2023-46498
- https://github.com/evershopcommerce/evershop

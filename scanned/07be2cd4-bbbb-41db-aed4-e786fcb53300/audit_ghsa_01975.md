# [M] Missing Authentication for Critical Function

## Summary
Severity: Medium
Advisory: GHSA-p696-gf58-9w97
CVE: CVE-2021-32709
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-p696-gf58-9w97
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.1.1

## Details
Shopware is an open source eCommerce platform. Creation of order credits was not validated by ACL in admin orders. Users are recommend to update to the current version 6.4.1.1. You can get the update to 6.4.1.1 regularly via the Auto-Updater or directly via the download overview. For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/platform/security/advisories/GHSA-g7w8-pp9w-7p32
- https://nvd.nist.gov/vuln/detail/CVE-2021-32709
- https://www.shopware.com/en/changelog/#6-4-1-1

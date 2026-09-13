# [H] Shopware database password is leaked to an unauthenticated users

## Summary
Severity: High
Advisory: GHSA-r4ph-mx67-x58p
CVE: CVE-2020-13997
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r4ph-mx67-x58p
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.0.0 <6.2.3
- Packagist: `shopware/platform` — affected >=6.0.0 <6.2.3

## Details
In Shopware 6 before 6.2.3, the database password is leaked to an unauthenticated user when a DriverException occurs and verbose error handling is enabled. This vulnerability does not affect the shopware 5 release branch (`shopware/shopware` on packagist).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13997
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-07-2020
- https://github.com/shopware/shopware
- https://www.shopware.com/en/changelog/#6-2-3

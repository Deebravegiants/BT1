# [M] Cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-7vmw-7x57-q6jw
CVE: CVE-2021-32713
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-7vmw-7x57-q6jw
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=0 <5.6.10

## Details
Shopware is an open source eCommerce platform. Versions prior to 5.6.10 suffer from an authenticated stored XSS in administration vulnerability. Users are recommend to update to the version 5.6.10. You can get the update to 5.6.10 regularly via the Auto-Updater or directly via the download overview.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-f6p7-8xfw-fjqq
- https://nvd.nist.gov/vuln/detail/CVE-2021-32713
- https://github.com/shopware/shopware/commit/a0850ffbc6f581a8eb8425cc2bf77a0715e21e12
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-05-2021

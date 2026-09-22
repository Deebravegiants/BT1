# [M] Insecure direct object reference of log files of the Import/Export feature

## Summary
Severity: Medium
Advisory: GHSA-54gp-qff8-946c
CVE: CVE-2021-37709
CWE: CWE-532, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-54gp-qff8-946c
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.3.1
- Packagist: `shopware/core` — affected >=0 <6.4.3.1

## Details
### Impact
Insecure direct object reference of log files of the Import/Export feature

### Patches
We recommend updating to the current version 6.4.3.1. You can get the update to 6.4.3.1 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

### Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659

## References
- https://github.com/shopware/platform/security/advisories/GHSA-54gp-qff8-946c
- https://nvd.nist.gov/vuln/detail/CVE-2021-37709
- https://github.com/shopware/platform/commit/a9f52abb6eb503654c492b6b2076f8d924831fec
- https://github.com/shopware/platform

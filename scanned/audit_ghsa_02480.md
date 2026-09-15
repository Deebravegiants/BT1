# [H] Command injection in mail agent settings

## Summary
Severity: High
Advisory: GHSA-xh55-2fqp-p775
CVE: CVE-2021-37708
CWE: CWE-77, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-xh55-2fqp-p775
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.3.1
- Packagist: `shopware/core` — affected >=0 <6.4.3.1

## Details
### Impact
Command injection in mail agent settings

### Patches
We recommend updating to the current version 6.4.3.1. You can get the update to 6.4.3.1 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

### Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659

## References
- https://github.com/shopware/platform/security/advisories/GHSA-xh55-2fqp-p775
- https://nvd.nist.gov/vuln/detail/CVE-2021-37708
- https://github.com/shopware/platform/commit/82d8d1995f6ce9054323b2c3522b1b3cf04853aa
- https://github.com/shopware/platform

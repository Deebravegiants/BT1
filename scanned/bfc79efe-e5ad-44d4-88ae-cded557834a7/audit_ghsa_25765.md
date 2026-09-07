# [M] HTML injection possibility in voucher code form in Shopware

## Summary
Severity: Medium
Advisory: GHSA-952p-fqcp-g8pc
CVE: CVE-2022-24746
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-10
Source: https://github.com/advisories/GHSA-952p-fqcp-g8pc
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.8.1
- Packagist: `shopware/core` — affected >=0 <6.4.8.1
- Packagist: `shopware/storefront` — affected >=0 <6.4.8.1

## Details
### Impact
HTML injection possibility in voucher code form

## Patches
Patched in 6.4.8.1, maintainers recommend updating to the current version 6.4.8.2. You can get the update to 6.4.8.2 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

## Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/platform/security/advisories/GHSA-952p-fqcp-g8pc
- https://nvd.nist.gov/vuln/detail/CVE-2022-24746
- https://github.com/shopware/platform/commit/651598a61073cbe59368e311817bdc6e7fb349c6
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-02-2022
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-02-2022?category=security-updates
- https://github.com/shopware/platform

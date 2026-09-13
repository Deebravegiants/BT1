# [M] Internal hidden fields are visible on to many associations in admin api

## Summary
Severity: Medium
Advisory: GHSA-gpmh-g94g-qrhr
Ecosystem: Packagist
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-gpmh-g94g-qrhr
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.1.1
- Packagist: `shopware/core` — affected >=0 <6.4.1.1

## Details
### Impact
The admin api has exposed some internal hidden fields when an association has been loaded with a to many reference

### Patches
We recommend updating to the current version 6.4.1.1. You can get the update to 6.4.1.1 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

### Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659

## References
- https://github.com/shopware/platform/security/advisories/GHSA-gpmh-g94g-qrhr

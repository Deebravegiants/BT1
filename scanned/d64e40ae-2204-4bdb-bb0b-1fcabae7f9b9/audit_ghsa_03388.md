# [M] Exposure of .env if project root is configured as web root in shopware/production

## Summary
Severity: Medium
Advisory: GHSA-3pcr-4982-548m
CWE: CWE-552
Ecosystem: Packagist
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-3pcr-4982-548m
Type: github-advisory

## Affected
- Packagist: `shopware/production` — affected >=0 <6.3.5.3
- Packagist: `shopware/shopware` — affected >=0 <6.3.5.3

## Details
### Impact

The .env and other sensitive files can be leaked if the project root and not `/public` is configured as the web root.

### Patches
We recommend to update to the current version 6.3.5.3. You can get the update to 6.3.5.3 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

### Workarounds

You should always use `/public` as the web root.

For older versions of 6.1 and 6.2, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659

### For more information
https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-04-2021

## References
- https://github.com/shopware/platform/security/advisories/GHSA-3pcr-4982-548m
- https://github.com/shopware/shopware/security/advisories/GHSA-3pcr-4982-548m
- https://github.com/shopware/shopware

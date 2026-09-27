# [M] Authenticated remote code execution

## Summary
Severity: Medium
Advisory: GHSA-pjj4-jjgc-h3r8
CWE: CWE-74
Ecosystem: Packagist
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-pjj4-jjgc-h3r8
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.3.5.2

## Details
### Impact
Authenticated remote code execution using plugin manager without ACL permissions.

### Patches
We recommend to update to the current version 6.3.5.2. You can get the update to 6.3.5.2 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

### Workarounds
For older versions of 6.1 and 6.2, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659

### For more information
https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-03-2021

## References
- https://github.com/shopware/platform/security/advisories/GHSA-pjj4-jjgc-h3r8
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-03-2021

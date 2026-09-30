# [C] Webcache Poisoning in shopware/platform and shopware/core

## Summary
Severity: Critical
Advisory: GHSA-r64m-qchj-hrjp
CWE: CWE-444
Ecosystem: Packagist
Published: 2021-11-24
Source: https://github.com/advisories/GHSA-r64m-qchj-hrjp
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=0 <6.4.6.1
- Packagist: `shopware/platform` — affected >=0 <6.4.6.1

## Details
### Impact
Webcache Poisoning via X-Forwarded-Prefix and sub-request

### Patches
We recommend updating to the current version 6.4.6.1. You can get the update to 6.4.6.1 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659

## References
- https://github.com/shopware/platform/security/advisories/GHSA-r64m-qchj-hrjp
- https://github.com/shopware/platform/commit/9062f15450d183f2c666664841efd4f5ef25e0f3
- https://github.com/shopware/platform

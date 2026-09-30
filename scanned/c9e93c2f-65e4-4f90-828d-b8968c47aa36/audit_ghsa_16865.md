# [M] Shopware Improper Session Handling in store-api account logout

## Summary
Severity: Medium
Advisory: GHSA-5297-wrrp-rcj7
CVE: CVE-2024-31447
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-04-08
Source: https://github.com/advisories/GHSA-5297-wrrp-rcj7
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.3.5.0 <6.5.8.8
- Packagist: `shopware/platform` — affected >=6.3.5.0 <6.5.8.8
- Packagist: `shopware/core` — affected >=6.6.0.0-rc1 <6.6.1.0
- Packagist: `shopware/platform` — affected >=6.6.0.0-rc1 <6.6.1.0

## Details
### Impact

When a authentificated request is made to `POST /store-api/account/logout`, the cart will be cleared, but the User won't be logged out. This affects only the direct store-api usage, as the PHP Storefront listens additionally on `CustomerLogoutEvent` and invalidates the session additionally. 

### Patches
The problem has been fixed with Shopware 6.6.1.0 and 6.5.8.8.

### Workarounds
When you are not able to update, you can install the latest version of the Shopware Security Plugin.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-5297-wrrp-rcj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-31447
- https://github.com/shopware/shopware/commit/5cc84ddd817ad0c1d07f9b3c79ab346d50514a77
- https://github.com/shopware/shopware/commit/d29775aa758f70d08e0c5999795c7c26d230e7d3
- https://github.com/shopware/shopware

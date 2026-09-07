# [M] HTTP caching is marking private HTTP headers as public in Shopware

## Summary
Severity: Medium
Advisory: GHSA-6wrh-279j-6hvw
CVE: CVE-2022-24747
CWE: CWE-200, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-10
Source: https://github.com/advisories/GHSA-6wrh-279j-6hvw
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.8.2
- Packagist: `shopware/core` — affected >=0 <6.4.8.2
- Packagist: `shopware/storefront` — affected >=0 <6.4.8.2

## Details
### Impact
HTTP caching is marking private HTTP headers as public

## Patches
Fixed in  recommend updating to the current version 6.4.8.2. You can get the update to 6.4.8.2 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

## Workarounds
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/platform/security/advisories/GHSA-6wrh-279j-6hvw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24747
- https://github.com/shopware/platform/commit/d51863148f32306aafdbc7f9f48887c69fce206f
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-03-2022
- https://github.com/shopware/platform

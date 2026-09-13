# [M] Shopware guest session is shared between customers

## Summary
Severity: Medium
Advisory: GHSA-jp6h-mxhx-pgqh
CVE: CVE-2022-24745
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-10
Source: https://github.com/advisories/GHSA-jp6h-mxhx-pgqh
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.8.2
- Packagist: `shopware/storefront` — affected >=0 <6.4.8.2

## Details
### Impact
Guest sessions are shared between customers when HTTP cache is enabled. Setups with Varnish are not affected by this issue

## Patches

We recommend updating to the current version 6.4.8.2. You can get the update to 6.4.8.2 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

## Workarounds

### Security Plugin
For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

### Disable HTTP Cache

Disabling HTTP Cache is also a valid workaround

## References
- https://github.com/shopware/platform/security/advisories/GHSA-jp6h-mxhx-pgqh
- https://nvd.nist.gov/vuln/detail/CVE-2022-24745
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-03-2022?_ga=2.159980029.1931762803.1646933116-1088482757.1646933116
- https://github.com/shopware/platform

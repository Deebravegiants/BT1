# [H] Shopware allows Denial Of Service via password length

## Summary
Severity: High
Advisory: GHSA-cgfj-hj93-rmh2
CVE: CVE-2025-30151
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-cgfj-hj93-rmh2
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.6.0.0 <6.6.10.3
- Packagist: `shopware/platform` — affected >=6.6.0.0 <6.6.10.3
- Packagist: `shopware/core` — affected >=6.7.0.0-rc1 <6.7.0.0-rc2
- Packagist: `shopware/platform` — affected >=6.7.0.0-rc1 <6.7.0.0-rc2
- Packagist: `shopware/core` — affected >=0 <6.5.8.17
- Packagist: `shopware/platform` — affected >=0 <6.5.8.17

## Details
### Impact

It's possible to pass long passwords that leads to Denial Of Service via forms in Storefront forms or Store-API.

### Patches
Update to Shopware 6.6.10.3 or 6.5.8.17

### Workarounds
For older versions of 6.4, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-cgfj-hj93-rmh2
- https://nvd.nist.gov/vuln/detail/CVE-2025-30151
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.5.8.17
- https://github.com/shopware/shopware/releases/tag/v6.6.10.3
- https://github.com/shopware/shopware/releases/tag/v6.7.0.0-rc2

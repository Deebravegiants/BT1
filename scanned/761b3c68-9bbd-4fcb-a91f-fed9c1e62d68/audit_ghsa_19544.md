# [M] Shopware Broken ACL on Document retrieval to access other customers documents

## Summary
Severity: Medium
Advisory: GHSA-68wv-g3fw-pq7q
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-68wv-g3fw-pq7q
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
It's possible to guess the deepLinkCode of an Document to open documents of other customers

### Patches
Update to Shopware 6.6.10.3 or 6.5.8.17

### Workarounds
For older versions of 6.4, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-68wv-g3fw-pq7q
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.5.8.17
- https://github.com/shopware/shopware/releases/tag/v6.6.10.3
- https://github.com/shopware/shopware/releases/tag/v6.7.0.0-rc2

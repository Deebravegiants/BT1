# [M] Shopware vulnerable to Improper Access Control with ManyToMany associations in store-api

## Summary
Severity: Medium
Advisory: GHSA-hhcq-ph6w-494g
CVE: CVE-2024-42354
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-hhcq-ph6w-494g
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=0 <6.5.8.13
- Packagist: `shopware/platform` — affected >=0 <6.5.8.13
- Packagist: `shopware/core` — affected >=6.6.0.0 <6.6.5.1
- Packagist: `shopware/platform` — affected >=6.6.0.0 <6.6.5.1

## Details
### Impact

The store-API works with regular entities and not expose all fields for the public API; fields need to be marked as ApiAware in the EntityDefinition. So only ApiAware fields of the EntityDefinition will be encoded to the final JSON. 

The processing of the Criteria did not considered ManyToMany associations and so they were not considered properly and the protections didn't get used.

This issue cannot be reproduced with the default entities by Shopware, but can be triggered with extensions.

### Patches
Update to Shopware 6.6.5.1 or 6.5.8.13.

### Workarounds
For older versions of 6.2, 6.3,  and 6.4, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-hhcq-ph6w-494g
- https://nvd.nist.gov/vuln/detail/CVE-2024-42354
- https://github.com/shopware/core/commit/a784aa1cec0624e36e0ee4d41aeebaed40e0442f
- https://github.com/shopware/core/commit/d35ee2eda5c995faeb08b3dad127eab65c64e2a2
- https://github.com/shopware/shopware/commit/8504ba7e56e53add6a1d5b9d45015e3d899cd0ac
- https://github.com/shopware/shopware/commit/ad83d38809df457efef21c37ce0996430334bf01
- https://github.com/shopware/shopware

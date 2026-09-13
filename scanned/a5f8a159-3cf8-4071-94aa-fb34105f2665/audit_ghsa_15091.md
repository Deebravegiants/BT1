# [M] Broken Access Control order API in Shopware

## Summary
Severity: Medium
Advisory: GHSA-3867-jc5c-66qf
CVE: CVE-2024-22407
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-17
Source: https://github.com/advisories/GHSA-3867-jc5c-66qf
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=0 <6.5.7.4
- Packagist: `shopware/platform` — affected >=0 <6.5.7.4

## Details
### Impact

In the Shopware CMS, the state handler for orders fails to sufficiently verify user authorizations for actions that modify the payment, delivery, and/or order status. Due to this inadequate implementation, users lacking 'write' permissions for orders are still able to change the order state.

### Patches
Update to Shopware 6.5.7.4

### Workarounds
For older versions of 6.1, 6.2, 6.3 and 6.4 corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-3867-jc5c-66qf
- https://nvd.nist.gov/vuln/detail/CVE-2024-22407
- https://github.com/shopware/core/commit/78142489264f9262eaaa436ba036df40026a06be
- https://github.com/shopware/shopware/commit/fb25e24ca51650009ffa2520f1e67b48b911354a
- https://github.com/shopware/shopware

# [H] Shopware vulnerable to Server Side Template Injection in Twig using deprecation silence tag

## Summary
Severity: High
Advisory: GHSA-27wp-jvhw-v4xp
CVE: CVE-2024-42355
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-27wp-jvhw-v4xp
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=0 <6.5.8.13
- Packagist: `shopware/platform` — affected >=0 <6.5.8.13
- Packagist: `shopware/platform` — affected >=6.6.0.0 <6.6.5.1
- Packagist: `shopware/core` — affected >=6.6.0.0 <6.6.5.1

## Details
### Impact

Shopware has a new Twig Tag `sw_silent_feature_call` which silences deprecation messages while triggered in this tag.
It accepts as parameter a string the feature flag name to silence, but this parameter is not escaped properly and allows execution of code.

### Patches
Update to Shopware 6.6.5.1 or 6.5.8.13

### Workarounds
For older versions of 6.2, 6.3,  and 6.4, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-27wp-jvhw-v4xp
- https://nvd.nist.gov/vuln/detail/CVE-2024-42355
- https://github.com/shopware/core/commit/a784aa1cec0624e36e0ee4d41aeebaed40e0442f
- https://github.com/shopware/core/commit/d35ee2eda5c995faeb08b3dad127eab65c64e2a2
- https://github.com/shopware/shopware/commit/445c6763cc093fbd651e0efaa4150deae4ae60da
- https://github.com/shopware/shopware/commit/8504ba7e56e53add6a1d5b9d45015e3d899cd0ac
- https://github.com/shopware/shopware

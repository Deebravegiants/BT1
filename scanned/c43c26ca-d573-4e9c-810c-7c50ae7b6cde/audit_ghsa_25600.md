# [H] Server-Side Request Forgery (SSRF) in Shopware

## Summary
Severity: High
Advisory: GHSA-7gm7-8q8v-9gf2
CVE: CVE-2022-24871
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-7gm7-8q8v-9gf2
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.10.1
- Packagist: `shopware/core` — affected >=0 <6.4.10.1

## Details
### Impact

The  attacker can abuse the Admin SDK functionality on the server to read or update internal resources.

### Patches

We recommend updating to the current version 6.4.10.1. You can get the update to 6.4.10.1 regularly via the Auto-Updater or directly via the download overview.

https://www.shopware.com/en/download/#shopware-6

### Workarounds

For older versions of 6.1, 6.2, and 6.3, corresponding security measures are also available via a plugin. For the full range of functions, we recommend updating to the latest Shopware version.

## References
- https://github.com/shopware/platform/security/advisories/GHSA-7gm7-8q8v-9gf2
- https://nvd.nist.gov/vuln/detail/CVE-2022-24871
- https://github.com/shopware/platform/commit/083765e2d64a00315050c4891800c9e98ba0c77c
- https://docs.shopware.com/en/shopware-6-en/security-updates/security-update-04-2022
- https://github.com/shopware/platform

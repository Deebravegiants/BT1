# [H] Shopware Has Improper Control of Generation of Code in Twig rendered views

## Summary
Severity: High
Advisory: GHSA-7cw6-7h3h-v8pf
CVE: CVE-2026-23498
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-7cw6-7h3h-v8pf
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=6.7.0.0 <6.7.6.1
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.6.1

## Details
### Impact
We fixed with [CVE-2023-2017](https://github.com/advisories/GHSA-7v2v-9rm4-7m8f) Twig filters to only be executed with allowed functions. However there was a regression that lead to an array and array crafted PHP Closure not checked being against allow list for the map(...) override

### Patches
Patched in 6.7.6.1

### Workarounds
Install the security plugin

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-7cw6-7h3h-v8pf
- https://nvd.nist.gov/vuln/detail/CVE-2026-23498
- https://github.com/shopware/shopware/commit/3966b05590e29432b8485ba47b4fcd14dd0b8475
- https://github.com/advisories/GHSA-7v2v-9rm4-7m8f
- https://github.com/shopware/shopware

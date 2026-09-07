# [M] Potential XSS injection in the newsletter conditions field

## Summary
Severity: Medium
Advisory: GHSA-vwfx-hh3w-fj99
CVE: CVE-2021-21418
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-vwfx-hh3w-fj99
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_emailsubscription` — affected >=0 <2.6.1

## Details
### Impact
An employee can inject javascript in the newsletter condition field that will then be executed on the front office

### Patches
The issue has been fixed in 2.6.1

## References
- https://github.com/PrestaShop/ps_emailsubscription/security/advisories/GHSA-vwfx-hh3w-fj99
- https://nvd.nist.gov/vuln/detail/CVE-2021-21418
- https://github.com/PrestaShop/ps_emailsubscription/commit/664ffb225e2afb4a32640bbedad667dc6e660b70
- https://github.com/PrestaShop/ps_emailsubscription/releases/tag/v2.6.1
- https://packagist.org/packages/prestashop/ps_emailsubscription

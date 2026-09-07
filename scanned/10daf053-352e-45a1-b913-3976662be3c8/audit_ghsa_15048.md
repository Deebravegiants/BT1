# [H] PrestaShop some attribute not escaped in Validate::isCleanHTML method

## Summary
Severity: High
Advisory: GHSA-xgpm-q3mq-46rq
CVE: CVE-2024-21627
CWE: CWE-20, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-xgpm-q3mq-46rq
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.0.0-beta.1 <8.1.3
- Packagist: `prestashop/prestashop` — affected >=0 <1.7.8.11

## Details
### Description
Some event attributes are not detected by the isCleanHTML method

### Impact
Some modules using the isCleanHTML method could be vulnerable to xss

### Patches
8.1.3, 1.7.8.11

### Workarounds
The best workaround is to use the `HTMLPurifier` library to sanitize html input coming from users. The library is already available as a dependency in the PrestaShop project. Beware though that in legacy object models, fields of `HTML` type will call `isCleanHTML`.

### Reporters

Reported by Antonio Russo (@Antonio-R1 on GitHub) and Antonio Rocco Spataro (@antoniospataro on GitHub).

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-xgpm-q3mq-46rq
- https://nvd.nist.gov/vuln/detail/CVE-2024-21627
- https://github.com/PrestaShop/PrestaShop/commit/0ed1af8de500538490f88e9e794e2e8113fb8df7
- https://github.com/PrestaShop/PrestaShop/commit/73cfb44666818eefd501b526a894fe884dd12129
- https://github.com/PrestaShop/PrestaShop/commit/ba06d18466df5b92cb841d504cc7210121104883
- https://github.com/PrestaShop/PrestaShop/commit/f799dcff564cd1b7ead932ffc3343b675107dbce
- https://github.com/PrestaShop/PrestaShop

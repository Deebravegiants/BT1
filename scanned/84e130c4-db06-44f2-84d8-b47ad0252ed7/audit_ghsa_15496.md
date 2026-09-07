# [H] Pimcore includes vulnerable PHPOffice/PhpSpreadsheet

## Summary
Severity: High
Advisory: GHSA-hq76-662x-7mw4
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-hq76-662x-7mw4
Type: github-advisory

## Affected
- Packagist: `pimcore/data-importer` — affected >=0 <1.8.9
- Packagist: `pimcore/data-importer` — affected >=1.9.0 <1.9.3
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.3.11
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=1.4.0 <1.4.7
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=1.5.0 <1.5.4
- Packagist: `pimcore/pimcore` — affected >=10.6.9.0 <10.6.9.12
- Packagist: `pimcore/pimcore` — affected >=11.1.0.0 <11.1.6.11

## Details
### Summary
Pimcore 10.6.x and Enterprise 10.6.x versions currently depend on PHPOffice/PhpSpreadsheet version 1.x, which has recently been identified with a security vulnerability (CVE-2024-45048). To mitigate this issue, it is recommended to update to the latest version 2.2.2. For more details, please refer to the official advisory: [GHSA-ghg6-32f9-2jp7](https://github.com/advisories/GHSA-ghg6-32f9-2jp7).

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-hq76-662x-7mw4
- https://github.com/advisories/GHSA-ghg6-32f9-2jp7
- https://github.com/pimcore/pimcore

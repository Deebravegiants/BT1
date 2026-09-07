# [C] SQL filter bypass leading to arbitrary write requests using "SQL Manager"

## Summary
Severity: Critical
Advisory: GHSA-p379-cxqh-q822
CVE: CVE-2023-30839
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-25
Source: https://github.com/advisories/GHSA-p379-cxqh-q822
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.0.0 <8.0.4
- Packagist: `prestashop/prestashop` — affected >=0 <1.7.8.9

## Details
### Impact
SQL filtering vulnerability, a BO user can write, update and delete in the database, even without having specific rights.

### Patches
PrestaShop 8.0.4 and 1.7.8.9 will contain the patch.

### Workarounds
no

### References
no

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-p379-cxqh-q822
- https://nvd.nist.gov/vuln/detail/CVE-2023-30839
- https://github.com/PrestaShop/PrestaShop/commit/0f2a9b7fdd42d1dd3b21d4fad586a849642f3c30
- https://github.com/PrestaShop/PrestaShop/commit/d1d27dc371599713c912b71bc2a455cacd7f2149
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/1.7.8.9
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.0.4

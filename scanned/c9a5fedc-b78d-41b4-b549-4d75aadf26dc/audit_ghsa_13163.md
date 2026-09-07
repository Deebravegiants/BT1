# [M] PrestaShop allows employee without any access rights to list all installed modules

## Summary
Severity: Medium
Advisory: GHSA-gvrg-62jp-rf7j
CVE: CVE-2023-43664
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-gvrg-62jp-rf7j
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.1.2

## Details
### Impact
In BO, an employee can list all modules without any access rights: method `ajaxProcessGetPossibleHookingListForModule` doesn't check access rights

### Patches
Fixed on 8.1.2

### Workarounds

### References

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-gvrg-62jp-rf7j
- https://nvd.nist.gov/vuln/detail/CVE-2023-43664
- https://github.com/PrestaShop/PrestaShop/commit/15bd281c18f032a5134a8d213b44d24829d45762
- https://github.com/PrestaShop/PrestaShop

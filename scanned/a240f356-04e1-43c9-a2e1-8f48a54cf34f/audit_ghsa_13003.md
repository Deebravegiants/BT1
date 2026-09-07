# [M] PrestaShop path traversal

## Summary
Severity: Medium
Advisory: GHSA-m9r4-3fg7-pqm2
CVE: CVE-2023-39525
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-m9r4-3fg7-pqm2
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.1.1

## Details
### Impact
In the back office, files can be compromised using path traversal by replaying the import file deletion query with a specified file path, using traversal path.

### Patches
8.1.1

### Found by
Aleksey Solovev (Positive Technologies)

### Workarounds
none

### References
none

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-m9r4-3fg7-pqm2
- https://nvd.nist.gov/vuln/detail/CVE-2023-39525
- https://github.com/PrestaShop/PrestaShop/commit/c7c9a5110421bb2856f4d312ecce192d079b5ec7
- https://github.com/PrestaShop/PrestaShop

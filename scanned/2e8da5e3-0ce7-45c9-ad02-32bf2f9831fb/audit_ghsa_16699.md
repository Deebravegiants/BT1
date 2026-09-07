# [M] Anonymous PrestaShop customer can download other customers' invoices

## Summary
Severity: Medium
Advisory: GHSA-7pjr-2rgh-fc5g
CVE: CVE-2024-34717
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-7pjr-2rgh-fc5g
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.1.5 <8.1.6

## Details
### Impact
Since PrestaShop 8.1.5, any invoice can be downloaded from front-office in anonymous mode, by supplying a random secure_key parameter in the url.

### Patches
Patched in 8.1.6

### Workarounds
Upgrade to 8.1.6

Thank you to Samuel Bodevin, who found this vulnerability and shared it with the PrestaShop team.

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-7pjr-2rgh-fc5g
- https://nvd.nist.gov/vuln/detail/CVE-2024-34717
- https://github.com/PrestaShop/PrestaShop/commit/46b9a2b430dd2008ac061fbcbae9f7af55a7920a
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.1.6

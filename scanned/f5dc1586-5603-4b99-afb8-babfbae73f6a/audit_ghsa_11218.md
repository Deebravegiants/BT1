# [H] PrestaShop has multiple stored XSS vulnerabilities via unprotected Template variables

## Summary
Severity: High
Advisory: GHSA-35pf-37c6-jxjv
CVE: CVE-2026-33673
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-35pf-37c6-jxjv
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=9.0.0-alpha.1 <9.1.0
- Packagist: `prestashop/prestashop` — affected >=0 <8.2.5

## Details
### Impact
Multiple stored Cross-Site Scripting (stored XSS) vulnerabilities in the BO: an attacker who can inject data into the database, via limited back-office access or a previously existing vulnerability, can exploit unprotected variables in back-office templates.

### Patches
Patched on 8.2.5 and 9.1.0

### Workarounds
None

### References
None

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-35pf-37c6-jxjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33673
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.2.5
- https://github.com/PrestaShop/PrestaShop/releases/tag/9.1.0

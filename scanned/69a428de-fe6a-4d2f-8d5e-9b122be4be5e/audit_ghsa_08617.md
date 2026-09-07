# [C] PrestaShop has a stored XSS executable in customer service view

## Summary
Severity: Critical
Advisory: GHSA-w9f3-qc75-qgx9
CVE: CVE-2026-44212
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-w9f3-qc75-qgx9
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.2.6
- Packagist: `prestashop/prestashop` — affected >=9.0.0 <9.1.1

## Details
### Impact

This is a **stored Cross-site Scripting (XSS)** vulnerability in the PrestaShop back-office Customer Service view.

An unauthenticated attacker can submit the public Contact Us form with a malicious email address. The payload is stored in the database and executed when a back-office employee opens the affected customer thread, enabling session hijacking and full back-office takeover.

### Patches

Patched in PrestaShop 8.2.6 and 9.1.1.

### Workarounds

None.

### Resources

- Reported by Savio at Doyensec (`anthropic@doyensec.com`) in collaboration with Anthropic Research.

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-w9f3-qc75-qgx9
- https://github.com/PrestaShop/PrestaShop

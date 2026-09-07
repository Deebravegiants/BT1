# [M] PrestaShop XSS can be stored in DB from "add a message form" in order detail page (FO)

## Summary
Severity: Medium
Advisory: GHSA-vr7m-r9vm-m4wf
CVE: CVE-2024-21628
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-vr7m-r9vm-m4wf
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.1.3

## Details
### Impact
The isCleanHtml method is not used on this this form, which makes it possible to store an xss in DB.
The impact is low because the html is not interpreted in BO, thanks to twig's escape mechanism.
In FO, the xss is effective, but only impacts the customer sending it, or the customer session from which it was sent.

Be careful if you have a module fetching these messages from the DB and displaying it without escaping html.

### Patches
8.1.x

### Reporter
Reported by Rona Febriana (linkedin: https://www.linkedin.com/in/rona-febriana/)

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-vr7m-r9vm-m4wf
- https://nvd.nist.gov/vuln/detail/CVE-2024-21628
- https://github.com/PrestaShop/PrestaShop/commit/afc45b93b3cc33be0e571559d2838c6960d98856
- https://github.com/PrestaShop/PrestaShop/commit/c3d78b7e49f5fe49a9d07725c3174d005deaa597
- https://github.com/PrestaShop/PrestaShop

# [C] PrestaShop cross-site scripting via customer contact form in FO, through file upload

## Summary
Severity: Critical
Advisory: GHSA-45vm-3j38-7p78
CVE: CVE-2024-34716
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-45vm-3j38-7p78
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=8.1.0 <8.1.6

## Details
### Impact
Only PrestaShops with customer-thread feature flag enabled are impacted, starting from PrestaShop 8.1.0.

The impact is substantial, when the customer thread feature flag is enabled, through the front-office contact form, a hacker can upload a malicious file containing an XSS that will be executed when an admin opens the attached file in back office.

Consequence: the script injected can access the session and the security token, which allows it to perform any authenticated action in the scope of the administrator's right.

### Patches
This vulnerability is patched in 8.1.6.

### Workarounds
As long as you have not upgraded to 8.1.6, a simple workaround is to disable the customer-thread feature-flag.

Thank you to Ayoub AIT ELMOKHTAR, who discovered this vulnerability and share it with the PrestaShop team.

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-45vm-3j38-7p78
- https://nvd.nist.gov/vuln/detail/CVE-2024-34716
- https://github.com/PrestaShop/PrestaShop/commit/a248898655e56cbcc6c308a5f1c8752231624bae
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.1.6

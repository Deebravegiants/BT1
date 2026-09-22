# [M] Presta Shop vulnerable to email enumeration 

## Summary
Severity: Medium
Advisory: GHSA-8xx5-h6m3-jr33
CVE: CVE-2025-51586
CWE: CWE-203, CWE-359
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-8xx5-h6m3-jr33
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.2.3

## Details
### Impact
An unauthenticated attacker with access to the back-office URL can manipulate the id_employee and reset_token parameters to enumerate valid back-office employee email addresses.

Impacted parties:
Store administrators and employees: their email addresses are exposed.
Merchants: risk of phishing, social engineering, and brute-force attacks targeting admin accounts.

### Patches
PrestaShop 8.2.3

### Workarounds
You must upgrade, or at least apply the changes from the PrestaShop 8.2.3 patch. More information: https://build.prestashop-project.org/news/2025/prestashop-8-2-3-security-release/

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-8xx5-h6m3-jr33
- https://nvd.nist.gov/vuln/detail/CVE-2025-51586
- https://github.com/PrestaShop/PrestaShop/commit/c97bdf10f77fedbe5a61a1dec5f96b3abb1d76fb
- https://build.prestashop-project.org/news/2025/prestashop-8-2-3-security-release
- https://github.com/PrestaShop/PrestaShop
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.2.1
- https://github.com/PrestaShop/PrestaShop/releases/tag/8.2.3
- https://maxime-morel.github.io/advisories/2025/CVE-2025-51586.md
- https://prestashop.com

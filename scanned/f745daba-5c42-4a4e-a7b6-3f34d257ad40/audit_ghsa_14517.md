# [M] Possible CSRF token fixation

## Summary
Severity: Medium
Advisory: GHSA-3g43-x7qr-96ph
CVE: CVE-2023-25170
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-3g43-x7qr-96ph
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.0.1

## Details
### Impact
When authenticating users PrestaShop preserves session attributes. Because this does not clear CSRF tokens upon login, this might enables `same-site attackers` to bypass the CSRF protection mechanism by performing an attack similar to a session-fixation.

### Patches
The problem is fixed in version 8.0.1

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-3g43-x7qr-96ph
- https://nvd.nist.gov/vuln/detail/CVE-2023-25170
- https://github.com/PrestaShop/PrestaShop

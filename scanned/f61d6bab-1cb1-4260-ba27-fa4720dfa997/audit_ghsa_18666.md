# [M] PrestaShop Checkout Backoffice directory traversal allows arbitrary file disclosure

## Summary
Severity: Medium
Advisory: GHSA-fpxp-pfqm-x54w
CVE: CVE-2025-61923
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-fpxp-pfqm-x54w
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_checkout` — affected >=0 <4.4.1
- Packagist: `prestashop/ps_checkout` — affected >=5.0.0 <5.0.5

## Details
# Impact
Missing validation on input vulnerable to directory traversal.

# Patches
The problem has been patched in versions:

v4.4.1 for PrestaShop 1.7 (build number: 7.4.4.1)
v4.4.1 for PrestaShop 8 (build number: 8.4.4.1)
v5.0.5 for PrestaShop 1.7 (build number: 7.5.0.5)
v5.0.5 for PrestaShop 8 (build number: 8.5.0.5)
v5.0.5 for PrestaShop 9 (build number: 9.5.0.5)

Read the [Versioning policy](https://github.com/PrestaShopCorp/ps_checkout/wiki/Versioning) to learn more about the build number.

# Credits
[Léo CUNÉAZ](https://github.com/inem0o) for reportied this issue.

## References
- https://github.com/PrestaShopCorp/ps_checkout/security/advisories/GHSA-fpxp-pfqm-x54w
- https://nvd.nist.gov/vuln/detail/CVE-2025-61923
- https://github.com/PrestaShopCorp/ps_checkout

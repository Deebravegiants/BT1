# [C] PrestaShop Checkout allows customer account takeover via email

## Summary
Severity: Critical
Advisory: GHSA-54hq-mf6h-48xh
CVE: CVE-2025-61922
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-54hq-mf6h-48xh
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_checkout` — affected >=1.3.0 <4.4.1
- Packagist: `prestashop/ps_checkout` — affected >=5.0.0 <5.0.5

## Details
# Impact
Missing validation on Express Checkout feature allows silent log-in

## Affected versions

The issue was introduced in PrestaShop Checkout 1.3.0 .

All versions above 1.3.0 are vulnerable except of course the patch versions published on 16/10/2025: 7.4.4.1, 8.4.4.1, 7.5.0.5, 8.5.0.5, 9.5.0.5

# Patches
The problem has been patched in versions

- v4.4.1 for PrestaShop 1.7 (build number: 7.4.4.1)
- v4.4.1 for PrestaShop 8 (build number: 8.4.4.1)
- v5.0.5 for PrestaShop 1.7 (build number: 7.5.0.5)
- v5.0.5 for PrestaShop 8 (build number: 8.5.0.5)
- v5.0.5 for PrestaShop 9 (build number: 9.5.0.5)

Read our [Versioning policy](https://github.com/PrestaShopCorp/ps_checkout/wiki/Versioning) to learn more about our build numbers and versions of PrestaShop Checkout

# Credits
We would like to thank [Léo CUNÉAZ](https://github.com/inem0o) for reporting the issue.

## References
- https://github.com/PrestaShopCorp/ps_checkout/security/advisories/GHSA-54hq-mf6h-48xh
- https://nvd.nist.gov/vuln/detail/CVE-2025-61922
- https://github.com/PrestaShopCorp/ps_checkout

# [M] Shopware vulnerable to persistent cross site scripting (XSS) in customer module

## Summary
Severity: Medium
Advisory: GHSA-5834-xv5q-cgfw
CVE: CVE-2022-31148
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-27
Source: https://github.com/advisories/GHSA-5834-xv5q-cgfw
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.7.0 <5.7.14

## Details
### Impact
Persistent XSS in customer module

### Patches

We recommend updating to the current version 5.7.14. You can get the update to 5.7.14 regularly via the Auto-Updater or directly via the download overview.

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html

### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-07-2022

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-5834-xv5q-cgfw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31148
- https://github.com/shopware/shopware/commit/7875855005648fba7b39371a70816afae2e07daf
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-07-2022
- https://github.com/shopware/shopware
- https://www.shopware.com/en/changelog-sw5/#5-7-14

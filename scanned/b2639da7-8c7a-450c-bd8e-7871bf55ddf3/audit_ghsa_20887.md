# [M] Shopware contains sensitive data in backend customer module

## Summary
Severity: Medium
Advisory: GHSA-6vfq-jmxg-g58r
CVE: CVE-2022-36101
CWE: CWE-200, CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-6vfq-jmxg-g58r
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=0 <5.7.15

## Details
### Impact
The request for the customer detail view in the backend administration contained sensitive data like the hashed password and the session ID.

### Patches
We recommend updating to the current version 5.7.15. You can get the update to 5.7.15 regularly via the Auto-Updater or directly via the download overview.
https://www.shopware.com/en/changelog-sw5/#5-7-15

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html


### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-09-2022

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-6vfq-jmxg-g58r
- https://nvd.nist.gov/vuln/detail/CVE-2022-36101
- https://github.com/shopware/shopware/commit/af5cdbc81d60f21b728e1433aeb8837f25938d2a
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-09-2022
- https://github.com/shopware/shopware
- https://packagist.org/packages/shopware/shopware

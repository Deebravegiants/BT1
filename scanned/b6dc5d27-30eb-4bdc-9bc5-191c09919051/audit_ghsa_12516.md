# [M] Shopware improper mail validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gh66-fp7j-98v5
CVE: CVE-2023-34099
CWE: CWE-754
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-06-28
Source: https://github.com/advisories/GHSA-gh66-fp7j-98v5
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.1.4 <5.7.18

## Details
### Impact
The mail validation in the registration process had some flaws, so it was possible to construct different mail addresses, that in the end result in the same address, which is shared by multiple accounts. 

### Patches
We recommend updating to the current version 5.7.18. You can get the update to 5.7.18 regularly via the Auto-Updater or directly via the release page.
https://github.com/shopware5/shopware/releases/tag/v5.7.18

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html


### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-06-2023

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-gh66-fp7j-98v5
- https://github.com/shopware5/shopware/security/advisories/GHSA-gh66-fp7j-98v5
- https://nvd.nist.gov/vuln/detail/CVE-2023-34099
- https://github.com/shopware5/shopware/commit/39cc714d9a0be33b43877044d0b88ea3c6b43f3d
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-06-2023
- https://github.com/shopware5/shopware
- https://www.shopware.com/en/changelog-sw5/#5-7-18

# [H] Malfunction of CSRF token validation in Shopware

## Summary
Severity: High
Advisory: GHSA-pf38-v6qj-j23h
CVE: CVE-2022-24879
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-pf38-v6qj-j23h
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.2.0 <5.7.9

## Details
### Impact
The CSRF tokens were not renewed after login and logout.
An attacker could impersonate the victim if the attacker is able to use the same device as the victim used beforehand.

### Patches
We recommend updating to the current version 5.7.9. You can get the update to 5.7.9 regularly via the Auto-Updater or directly via the download overview.
https://www.shopware.com/en/changelog-sw5/#5-7-9

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html


### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-04-2022

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-pf38-v6qj-j23h
- https://nvd.nist.gov/vuln/detail/CVE-2022-24879
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-04-2022
- https://github.com/shopware/shopware
- https://www.shopware.com/en/changelog-sw5/#5-7-9

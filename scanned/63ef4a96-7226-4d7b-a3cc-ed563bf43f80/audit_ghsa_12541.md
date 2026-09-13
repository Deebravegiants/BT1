# [M] Shopware dependency configuration exposed

## Summary
Severity: Medium
Advisory: GHSA-q97c-2mh3-pgw9
CVE: CVE-2023-34098
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-28
Source: https://github.com/advisories/GHSA-q97c-2mh3-pgw9
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.6.0 <5.7.18

## Details
### Impact
Due to a wrong configuration in the `.htaccess` file, the configuration file of Javascript dependencies could be read in production environments (`themes/package-lock.json`). With this information, the used Shopware version might be determined by an attacker, which could be used for further attacks. 

### Patches
We recommend updating to the current version 5.7.18. You can get the update to 5.7.18 regularly via the Auto-Updater or directly via the release page.
https://github.com/shopware5/shopware/releases/tag/v5.7.18

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html


### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-06-2023

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-q97c-2mh3-pgw9
- https://github.com/shopware5/shopware/security/advisories/GHSA-q97c-2mh3-pgw9
- https://nvd.nist.gov/vuln/detail/CVE-2023-34098
- https://github.com/shopware5/shopware/commit/b3518c8d9562a38615d638f31f79829f6e2f4b6a
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-06-2023
- https://github.com/shopware5/shopware
- https://www.shopware.com/en/changelog-sw5/#5-7-18

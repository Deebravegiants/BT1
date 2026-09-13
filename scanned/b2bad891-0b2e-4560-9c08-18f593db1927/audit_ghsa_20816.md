# [M] Shopware access control list bypassed via crafted specific URLs

## Summary
Severity: Medium
Advisory: GHSA-qc43-pgwq-3q2q
CVE: CVE-2022-36102
CWE: CWE-281
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-qc43-pgwq-3q2q
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=0 <5.7.15

## Details
### Impact
If backend admin controllers are called with a certain notation, the ACL could be bypassed. Users could execute actions, which they are normally not able to do.

### Patches
We recommend updating to the current version 5.7.15. You can get the update to 5.7.15 regularly via the Auto-Updater or directly via the download overview.
https://www.shopware.com/en/changelog-sw5/#5-7-15

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html


### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-09-2022

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-qc43-pgwq-3q2q
- https://nvd.nist.gov/vuln/detail/CVE-2022-36102
- https://github.com/shopware/shopware/commit/de92d3a78279119a5bbe203054f8fa1d25126af6
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-09-2022
- https://github.com/shopware/shopware
- https://packagist.org/packages/shopware/shopware

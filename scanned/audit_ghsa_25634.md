# [M] Multiple valid tokens for password reset in Shopware

## Summary
Severity: Medium
Advisory: GHSA-3qrq-r688-vvh4
CVE: CVE-2022-24892
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-3qrq-r688-vvh4
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=5.0.4 <5.7.9

## Details
### Impact
Multiple tokens for password reset could be requested. All tokens could be used to change the password.
This makes it possible for an attacker to take over the victims account if s/he gains access to the victims email account and finds unused password reset token in the emails within the time frame of two hours.

### Patches
We recommend updating to the current version 5.7.9. You can get the update to 5.7.9 regularly via the Auto-Updater or directly via the download overview.
https://www.shopware.com/en/changelog-sw5/#5-7-9

For older versions you can use the Security Plugin:
https://store.shopware.com/en/swag575294366635f/shopware-security-plugin.html


### References
https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-04-2022

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-3qrq-r688-vvh4
- https://nvd.nist.gov/vuln/detail/CVE-2022-24892
- https://docs.shopware.com/en/shopware-5-en/security-updates/security-update-04-2022
- https://github.com/shopware/shopware
- https://www.shopware.com/en/changelog-sw5/#5-7-9

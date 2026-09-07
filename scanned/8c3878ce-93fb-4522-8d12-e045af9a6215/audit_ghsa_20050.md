# [C] TYPO3 vulnerable to Insufficient Session Expiration

## Summary
Severity: Critical
Advisory: GHSA-53mm-hx32-6475
CVE: CVE-2022-47406
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-53mm-hx32-6475
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <2.0.5
- Packagist: `typo3/cms` — affected >=3.0.0 <3.0.3
- Packagist: `derhansen/fe_change_pwd` — affected >=3.0.0 <3.0.3
- Packagist: `derhansen/fe_change_pwd` — affected >=0 <2.0.5

## Details
An issue was discovered in the fe_change_pwd (aka Change password for frontend users) extension before 2.0.5, and 3.x before 3.0.3, for TYPO3. The extension fails to revoke existing sessions for the current user when the password has been changed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47406
- https://github.com/FriendsOfPHP/security-advisories/blob/master/derhansen/fe_change_pwd/CVE-2022-47406.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-ext-sa-2022-016

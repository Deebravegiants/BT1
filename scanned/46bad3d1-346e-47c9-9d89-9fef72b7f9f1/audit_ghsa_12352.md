# [M] Broken Access Control in extension "femanager" 

## Summary
Severity: Medium
Advisory: GHSA-4xp5-hr35-84cx
CVE: CVE-2023-50459
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-4xp5-hr35-84cx
Type: github-advisory

## Affected
- Packagist: `in2code/femanager` — affected >=7.0.0 <7.2.3

## Details
The extension fails to check access permissions for the edit user component. An authenticated frontend user can use the vulnerability to either edit data of various frontend users or to delete various frontend user accounts.

Another missing access check in the backend module of the extensions allows an authenticated backend user to perform various actions (userLogout, confirmUser, refuseUser and resendUserConfirmation) for any frontend user in the system.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/in2code/femanager/CVE-2023-50459.yaml
- https://typo3.org/security/advisory/typo3-ext-sa-2023-010

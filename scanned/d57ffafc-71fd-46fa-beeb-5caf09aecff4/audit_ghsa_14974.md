# [H] Privilege Escalation & SQL Injection in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-7qwg-fcpw-xg5g
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-7qwg-fcpw-xg5g
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.5.0 <8.7.17
- Packagist: `typo3/cms` — affected >=9.0.0 <9.3.2

## Details
Failing to properly dissociate system related configuration from user generated configuration, the Form Framework (system extension "form") is vulnerable to SQL injection and Privilege Escalation. Basically instructions can be persisted to a form definition file that were not configured to be modified - this applies to definitions managed using the form editor module as well as direct file upload using the regular file list module. A valid backend user account as well as having system extension form activated are needed in order to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-07-12-3.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-003

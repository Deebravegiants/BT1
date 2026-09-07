# [M] TYPO3 CMS missing check for expiration time of password reset token for backend users

## Summary
Severity: Medium
Advisory: GHSA-5959-4x58-r8c2
CVE: CVE-2022-36106
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-5959-4x58-r8c2
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.4.0 <10.4.32
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.16
- Packagist: `typo3/cms` — affected >=10.4.0 <10.4.32
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.16

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N/E:F/RL:O/RC:C` (5.0)

### Problem
It has been discovered that the expiration time of a password reset link for TYPO3 backend users has never been evaluated. As a result, a password reset link could be used to perform a password reset even if the default expiry time of two hours has been exceeded.

### Solution
Update to TYPO3 version 10.4.32 or 11.5.16 that fix the problem described above.

### Credits
Thanks to Ingo Fabbri who reported this issue and to TYPO3 security team member Torben Hansen who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-008](https://typo3.org/security/advisory/typo3-core-sa-2022-008)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-5959-4x58-r8c2
- https://nvd.nist.gov/vuln/detail/CVE-2022-36106
- https://github.com/TYPO3/typo3/commit/00b52a443b21baaaab35f8606dbb0ce427261bb5
- https://github.com/TYPO3/typo3/commit/56af2bd3a432156c30af9be71c9d6f7ef3a6159a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-36106.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-36106.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-008

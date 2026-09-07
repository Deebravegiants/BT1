# [M] TYPO3 Cross-Site Scripting in Frontend User Login

## Summary
Severity: Medium
Advisory: GHSA-2rcw-9hrm-8q7q
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-2rcw-9hrm-8q7q
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.32
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.21
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.2

## Details
Failing to properly encode user input, login status display is vulnerable to cross-site scripting in the website frontend. A valid user account is needed in order to exploit this vulnerability - either a backend user or a frontend user having the possibility to modify their user profile.

Template patterns that are affected are

- ###FEUSER_[fieldName]### using system extension felogin
- <!--###USERNAME###--> for regular frontend rendering (pattern can be defined individually using TypoScript setting config.USERNAME_substToken)

## References
- https://github.com/TYPO3/typo3/commit/1c85fe70269e2ff8ecf0b6d5f16550c6cd0ddc78
- https://github.com/TYPO3/typo3/commit/373bec5d7d415f0764ebbadc7970610dc26da068
- https://github.com/TYPO3/typo3/commit/e4143195e1451630f058a58ab62d92135948a927
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-12-11-3.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-008

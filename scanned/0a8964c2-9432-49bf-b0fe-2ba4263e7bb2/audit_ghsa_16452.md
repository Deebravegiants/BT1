# [H] TYPO3 frontend login vulnerable to Session Fixation

## Summary
Severity: High
Advisory: GHSA-r9vc-jfmh-6j48
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-r9vc-jfmh-6j48
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.14
- Packagist: `typo3/cms` — affected >=7.0.0 <7.3.1

## Details
It has been discovered that TYPO3 is susceptible to session fixation. If a user authenticates while anonymous session data is present, the session id is not changed. This makes it possible for attackers to generate a valid session id, trick users into using this session id (e.g. by leveraging a different Cross-Site Scripting vulnerability) and then maybe getting access to an authenticated session.

## References
- https://github.com/TYPO3/typo3/commit/4c9aba94a930d56ab374693c9c5cc0458587278a
- https://github.com/TYPO3/typo3/commit/4f6e84bba3c13ea8b2652af1a4c47758aa0705f4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-07-01-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-003
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-003

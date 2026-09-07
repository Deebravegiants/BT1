# [M] Information Disclosure in TYPO3 Backend

## Summary
Severity: Medium
Advisory: GHSA-vpr3-rc99-2wpr
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-vpr3-rc99-2wpr
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.26
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.10
- Packagist: `typo3/cms` — affected >=8.0.0 <8.2.1

## Details
The TYPO3 backend module stores the username of an authenticated backend user in its cache files. By guessing the file path to the cache files it is possible to receive valid backend usernames.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-07-19-4.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-017
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-017

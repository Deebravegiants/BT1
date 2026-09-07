# [M] TYPO3 Information Disclosure of Installed Extensions

## Summary
Severity: Medium
Advisory: GHSA-f624-8hfq-5fh3
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-f624-8hfq-5fh3
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.23
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.4

## Details
It has been discovered that mechanisms used for configuration of RequireJS package loading are susceptible to information disclosure. This way a potential attack can retrieve additional information about installed system and third party extensions.

## References
- https://github.com/TYPO3/typo3/commit/889ed77d2905d8b17afd31c723a23240c978823f
- https://github.com/TYPO3/typo3/commit/c81cca9e419e7aaed551b9b9a8d012ba7bffb287
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-001

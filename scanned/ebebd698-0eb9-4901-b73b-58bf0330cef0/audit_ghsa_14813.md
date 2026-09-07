# [M] Insecure Unserialize in TYPO3 Import/Export

## Summary
Severity: Medium
Advisory: GHSA-xvcp-33rc-j8gq
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-xvcp-33rc-j8gq
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.26
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.10
- Packagist: `typo3/cms` — affected >=8.0.0 <8.2.1

## Details
Failing to properly validate incoming import data, the Import/Export component is susceptible to insecure unserialize. To exploit this vulnerability a valid backend user account is needed.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-07-19-2.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-015

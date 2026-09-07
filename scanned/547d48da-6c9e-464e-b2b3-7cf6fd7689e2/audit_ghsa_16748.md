# [H] TYPO3 may allow editors to change, create, or delete metadata of files not within their file mounts

## Summary
Severity: High
Advisory: GHSA-4r76-xr68-w7m7
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-4r76-xr68-w7m7
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.14
- Packagist: `typo3/cms` — affected >=7.0.0 <7.3.1

## Details
It has been discovered, that editors with access to file meta data table could change, create or delete metadata of files which are not within their file mounts.

## References
- https://github.com/TYPO3/typo3/commit/0decbf83c531cab77497429eb2edecf9a1038b25
- https://github.com/TYPO3/typo3/commit/bff9fa5945801d1d2c641ddc8eb86c6647549d80
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-07-01-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-002
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-002

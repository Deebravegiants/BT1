# [H] TYPO3 Denial of Service in Frontend Record Registration

## Summary
Severity: High
Advisory: GHSA-g585-crjf-vhwq
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-g585-crjf-vhwq
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.32
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.21

## Details
TYPO3’s built-in record registration functionality (aka `basic shopping cart`) using recs URL parameters is vulnerable to denial of service. Failing to properly ensure that anonymous user sessions are valid, attackers can use this vulnerability in order to create  an arbitrary amount of individual session-data records in the database.

## References
- https://github.com/TYPO3/typo3/commit/05011d1248c54d00960e344fd920a6246da92415
- https://github.com/TYPO3/typo3/commit/fc2b4b9fb978088267f83e73cd401d4371dd40e3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-12-11-7.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-012

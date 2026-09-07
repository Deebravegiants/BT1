# [M] Insecure Unserialize in TYPO3 Backend

## Summary
Severity: Medium
Advisory: GHSA-c7rj-92xr-wprg
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-c7rj-92xr-wprg
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.29
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.13
- Packagist: `typo3/cms` — affected >=8.0.0 <8.4.1

## Details
Failing to properly validate incoming data, the suggest wizard is susceptible to insecure unserialize. To exploit this vulnerability a valid backend user account is needed.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-11-22-1.yaml

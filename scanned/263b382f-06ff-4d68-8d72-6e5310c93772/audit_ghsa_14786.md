# [M] Authentication Bypass in TYPO3 Frontend

## Summary
Severity: Medium
Advisory: GHSA-mh3r-6cp5-hc2j
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-mh3r-6cp5-hc2j
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.2.0 <8.6.1

## Details
Due to late TCA initialization the authentication service fails to restrict frontend user according to the validation rules. Therefore it is possible to authenticate restricted (e.g. disabled) frontend users.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2017-02-28-1.yaml

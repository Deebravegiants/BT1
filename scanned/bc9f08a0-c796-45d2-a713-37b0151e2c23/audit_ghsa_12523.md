# [M] ke_search (aka Faceted Search) vulnerable to Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-f4m6-x2xj-jc7w
CVE: CVE-2023-35783
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-16
Source: https://github.com/advisories/GHSA-f4m6-x2xj-jc7w
Type: github-advisory

## Affected
- Packagist: `tpwd/ke_search` — affected >=5.0.0 <5.0.2
- Packagist: `tpwd/ke_search` — affected >=4.1.0 <4.6.6
- Packagist: `tpwd/ke_search` — affected >=0 <4.0.3

## Details
The ke_search (aka Faceted Search) extension before 4.0.3, 4.1.x through 4.6.x before 4.6.6, and 5.x before 5.0.2 for TYPO3 allows XSS via indexed data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35783
- https://github.com/tpwd/ke_search/commit/14fa0703c2469e04eb398be4ae6268ec6ad6e720
- https://github.com/tpwd/ke_search/commit/b0f05d7e7e207bc0d5051bd96f3ff43c5c3658c6
- https://github.com/tpwd/ke_search/commit/d81a1f2f3dcb612220d505b495bc2851b87f6f74
- https://github.com/FriendsOfPHP/security-advisories/blob/master/tpwd/ke_search/CVE-2023-35783.yaml
- https://github.com/tpwd/ke_search
- https://typo3.org/security/advisory/typo3-ext-sa-2023-004

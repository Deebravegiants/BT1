# [M] TYPO3 allows remote attackers to obtain the database name via a direct request

## Summary
Severity: Medium
Advisory: GHSA-q68v-vcjg-r3vp
CVE: CVE-2012-1607
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q68v-vcjg-r3vp
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.4.0
- Packagist: `typo3/cms` — affected >=4.5.0
- Packagist: `typo3/cms` — affected >=4.6.0

## Details
The Command Line Interface (CLI) script in TYPO3 4.4.0 through 4.4.13, 4.5.0 through 4.5.13, 4.6.0 through 4.6.6, 4.7, and 6.0 allows remote attackers to obtain the database name via a direct request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1607
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20120426034517/http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-001
- https://web.archive.org/web/20120527123559/http://www.securityfocus.com/bid/52771
- http://www.debian.org/security/2012/dsa-2445
- http://www.openwall.com/lists/oss-security/2012/03/30/4

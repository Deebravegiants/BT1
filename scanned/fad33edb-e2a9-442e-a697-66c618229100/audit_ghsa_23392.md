# [M] Typo3 API XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-w3v6-r62r-fvqh
CVE: CVE-2012-1608
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w3v6-r62r-fvqh
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.4.0 <4.4.14
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.14
- Packagist: `typo3/cms` — affected >=4.6.0 <4.6.7

## Details
The `t3lib_div::RemoveXSS` API method in TYPO3 4.4.0 through 4.4.13, 4.5.0 through 4.5.13, 4.6.0 through 4.6.6, 4.7, and 6.0 allows remote attackers to bypass the cross-site scripting (XSS) protection mechanism and inject arbitrary web script or HTML via non printable characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1608
- https://web.archive.org/web/20120527123559/http://www.securityfocus.com/bid/52771
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-001
- http://www.debian.org/security/2012/dsa-2445
- http://www.openwall.com/lists/oss-security/2012/03/30/4

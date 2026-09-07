# [M] TYPO3 leaks a hash secret in an error message

## Summary
Severity: Medium
Advisory: GHSA-c22j-84c7-cm77
CVE: CVE-2009-0815
CWE: CWE-200, CWE-209
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-c22j-84c7-cm77
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=3.3 <4.0.12
- Packagist: `typo3/cms` — affected >=4.1 <4.1.10
- Packagist: `typo3/cms` — affected >=4.2 <4.2.6

## Details
The jumpUrl mechanism in class.tslib_fe.php in TYPO3 3.3.x through 3.8.x, 4.0 before 4.0.12, 4.1 before 4.1.10, 4.2 before 4.2.6, and 4.3alpha1 leaks a hash secret (juHash) in an error message, which allows remote attackers to read arbitrary files by including the hash in a request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0815
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20091206080208/http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-002
- https://web.archive.org/web/20200915000000*/http://www.securitytracker.com/id?1021710
- http://www.debian.org/security/2009/dsa-1720
- http://www.openwall.com/lists/oss-security/2009/02/10/6

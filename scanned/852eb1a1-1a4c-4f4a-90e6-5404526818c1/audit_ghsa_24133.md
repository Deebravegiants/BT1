# [M] Typo3 Exception Handler XSS

## Summary
Severity: Medium
Advisory: GHSA-qfr3-29w6-hwpg
CVE: CVE-2012-2112
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qfr3-29w6-hwpg
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.4 <4.4.15
- Packagist: `typo3/cms` — affected >=4.5 <4.5.15
- Packagist: `typo3/cms` — affected >=4.6 <4.6.8
- Packagist: `typo3/cms` — affected 4.7

## Details
Cross-site scripting (XSS) vulnerability in the Exception Handler in TYPO3 4.4.x before 4.4.15, 4.5.x before 4.5.15, 4.6.x before 4.6.8, and 4.7 allows remote attackers to inject arbitrary web script or HTML via exception messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2112
- https://exchange.xforce.ibmcloud.com/vulnerabilities/74920
- https://web.archive.org/web/20120421201555/http://www.securityfocus.com/bid/53047
- http://lists.typo3.org/pipermail/typo3-announce/2012/000241.html
- http://lists.typo3.org/pipermail/typo3-announce/2012/000242.html
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-002
- http://www.debian.org/security/2012/dsa-2455
- http://www.openwall.com/lists/oss-security/2012/04/17/5
- http://www.openwall.com/lists/oss-security/2012/04/18/1

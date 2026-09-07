# [M] Typo3 API XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-94c2-g68f-9r98
CVE: CVE-2012-3530
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-94c2-g68f-9r98
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5 <4.5.19
- Packagist: `typo3/cms` — affected >=4.6 <4.6.12
- Packagist: `typo3/cms` — affected >=4.7 <4.7.4

## Details
Incomplete blacklist vulnerability in the `t3lib_div::quoteJSvalue` API function in TYPO3 4.5.x before 4.5.19, 4.6.x before 4.6.12 and 4.7.x before 4.7.4 allows remote attackers to conduct cross-site scripting (XSS) attacks via certain HTML5 JavaScript events.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3530
- https://exchange.xforce.ibmcloud.com/vulnerabilities/77794
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-004
- http://www.debian.org/security/2012/dsa-2537
- http://www.openwall.com/lists/oss-security/2012/08/22/8

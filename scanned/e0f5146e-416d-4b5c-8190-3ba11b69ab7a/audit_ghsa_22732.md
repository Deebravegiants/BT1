# [M] TYPO3 Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-66j3-66cp-6c2m
CVE: CVE-2010-5099
CWE: CWE-20, CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-66j3-66cp-6c2m
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.2.0 <4.2.16
- Packagist: `typo3/cms` — affected >=4.3.0 <4.3.9
- Packagist: `typo3/cms` — affected >=4.4.0 <4.4.5

## Details
The fileDenyPattern functionality in the PHP file inclusion protection API in TYPO3 4.2.x before 4.2.16, 4.3.x before 4.3.9, and 4.4.x before 4.4.5 does not properly filter file types, which allows remote attackers to bypass intended access restrictions and access arbitrary PHP files, as demonstrated using path traversal sequences with %00 null bytes and CVE-2010-3714 to read the TYPO3 encryption key from localconf.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-5099
- https://exchange.xforce.ibmcloud.com/vulnerabilities/64180
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20120801235059/http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-sa-2010-022
- http://blog.nibblesec.org/2010/12/typo3-sa-2010-020-typo3-sa-2010-022.html
- http://www.exploit-db.com/exploits/15856
- http://www.openwall.com/lists/oss-security/2011/01/13/2
- http://www.openwall.com/lists/oss-security/2012/05/10/7
- http://www.openwall.com/lists/oss-security/2012/05/11/3
- http://www.openwall.com/lists/oss-security/2012/05/12/5

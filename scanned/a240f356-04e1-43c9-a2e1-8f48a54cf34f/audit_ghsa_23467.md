# [M] TYPO3 Unrestricted File Upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f35p-hcwf-9f9f
CVE: CVE-2008-2717
CWE: CWE-434
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-f35p-hcwf-9f9f
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=4.0.0 <4.0.9
- Packagist: `typo3/cms-core` — affected >=4.1.0 <4.1.7
- Packagist: `typo3/cms-core` — affected >=4.2.0 <4.2.1

## Details
TYPO3 4.0.x before 4.0.9, 4.1.x before 4.1.7, and 4.2.x before 4.2.1, uses an insufficiently restrictive default fileDenyPattern for Apache, which allows remote attackers to bypass security restrictions and upload configuration files such as .htaccess, or conduct file upload attacks using multiple extensions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-2717
- https://exchange.xforce.ibmcloud.com/vulnerabilities/42988
- https://github.com/TYPO3-CMS/core
- https://web.archive.org/web/20080815050856/http://securityreason.com/securityalert/3945
- https://web.archive.org/web/20081201212626/http://secunia.com/advisories/30619
- https://web.archive.org/web/20081206030529/http://secunia.com/advisories/30660
- https://web.archive.org/web/20200228131005/http://www.securityfocus.com/bid/29657
- https://web.archive.org/web/20201208012148/http://www.securityfocus.com/archive/1/493270/100/0/threaded
- http://buzz.typo3.org/teams/security/article/advice-on-core-security-issue-regarding-filedenypattern
- http://typo3.org/teams/security/security-bulletins/typo3-20080611-1
- http://www.debian.org/security/2008/dsa-1596

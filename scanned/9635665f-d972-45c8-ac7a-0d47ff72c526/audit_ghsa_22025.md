# [H] TYPO3 Backend Command Injection via Shell Metacharacters in Uploaded File Name

## Summary
Severity: High
Advisory: GHSA-3cqw-pxgr-jhrm
CVE: CVE-2009-3631
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-3cqw-pxgr-jhrm
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=0
- Packagist: `typo3/cms-backend` — affected >=4.1.0 <4.1.13
- Packagist: `typo3/cms-backend` — affected >=4.2.0 <4.2.10
- Packagist: `typo3/cms-backend` — affected >=4.3alpha1 <4.3beta2

## Details
The Backend subcomponent in TYPO3 4.0.13 and earlier, 4.1.x before 4.1.13, 4.2.x before 4.2.10, and 4.3.x before 4.3beta2, when the DAM extension or ftp upload is enabled, allows remote authenticated users to execute arbitrary commands via shell metacharacters in a filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3631
- https://exchange.xforce.ibmcloud.com/vulnerabilities/53923
- https://github.com/TYPO3-CMS/backend
- https://web.archive.org/web/20101223093042/http://www.securityfocus.com/bid/36801
- http://marc.info/?l=oss-security&m=125632856206736&w=2
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-016

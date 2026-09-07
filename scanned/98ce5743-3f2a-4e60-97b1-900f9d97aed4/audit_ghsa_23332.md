# [M] Front End User Registration (sr_feuser_register) extension for TYPO3 allows remote attackers to obtain user names, passwords

## Summary
Severity: Medium
Advisory: GHSA-m646-h2pw-56h4
CVE: CVE-2012-5890
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m646-h2pw-56h4
Type: github-advisory

## Affected
- Packagist: `sjbr/sr-feuser-register` — affected >=0 <2.6.2

## Details
The Front End User Registration (sr_feuser_register) extension before 2.6.2 for TYPO3 allows remote attackers to obtain user names and passwords via the (1) edit perspective or (2) autologin feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5890
- https://exchange.xforce.ibmcloud.com/vulnerabilities/80145
- https://github.com/TYPO3-extensions/sr_feuser_register
- https://web.archive.org/web/20120715071728/http://typo3.org/teams/security/security-bulletins/typo3-extensions/typo3-ext-sa-2012-002
- http://forge.typo3.org/projects/extension-sr_feuser_register/repository/entry/trunk/ChangeLog
- http://forge.typo3.org/projects/extension-sr_feuser_register/repository/revisions/58720

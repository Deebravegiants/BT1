# [H] Frontend User Registration extension for TYPO3 does not properly verify access rights

## Summary
Severity: High
Advisory: GHSA-rjrq-93hp-22ww
CVE: CVE-2009-1264
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-rjrq-93hp-22ww
Type: github-advisory

## Affected
- Packagist: `sjbr/sr-feuser-register` — affected >=0 <2.5.21

## Details
Frontend User Registration (sr_feuser_register) extension 2.5.20 and earlier for TYPO3 does not properly verify access rights, which allows remote authenticated users to obtain sensitive information such as passwords via unknown attack vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-1264
- https://github.com/TYPO3-extensions/sr_feuser_register
- https://web.archive.org/web/20090527190538/http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-004
- https://web.archive.org/web/20200228205603/http://www.securityfocus.com/bid/34374
- http://typo3.org/extensions/repository/view/sr_feuser_register/2.5.21

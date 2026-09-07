# [M] ckeditor-wordcount-plugin vulnerable to Cross-site Scripting in Source Mode of Editor

## Summary
Severity: Medium
Advisory: GHSA-q9w4-w667-qqj4
CVE: CVE-2023-37905
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-10
Source: https://github.com/advisories/GHSA-q9w4-w667-qqj4
Type: github-advisory

## Affected
- npm: `ckeditor-wordcount-plugin` — affected >=0 <1.17.12

## Details
### Problem

It has been discovered that the `ckeditor-wordcount-plugin` plugin for CKEditor4 is susceptible to cross-site scripting when switching to the source code mode.

### Solution

Update to version 1.17.12 of the `ckeditor-wordcount-plugin` plugin.

### Credits

* @sypets for reporting this finding to the TYPO3 Security Team
* @ohader for fixing the issue on behalf of the TYPO3 Security Team

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-m8fw-p3cr-6jqc
- https://github.com/w8tcha/CKEditor-WordCount-Plugin/security/advisories/GHSA-q9w4-w667-qqj4
- https://nvd.nist.gov/vuln/detail/CVE-2023-37905
- https://github.com/w8tcha/CKEditor-WordCount-Plugin/commit/0f03b3e5b7c1409998a13aba3a95396e6fa349d8
- https://github.com/w8tcha/CKEditor-WordCount-Plugin/commit/a4b154bdf35b3465320136fcb078f196b437c2f1
- https://github.com/w8tcha/CKEditor-WordCount-Plugin
- https://typo3.org/security/advisory/typo3-core-sa-2023-004

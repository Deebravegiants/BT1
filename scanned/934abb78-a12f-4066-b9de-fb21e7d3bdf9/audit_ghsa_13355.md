# [M] Cross-Site Scripting in CKEditor4 WordCount Plugin

## Summary
Severity: Medium
Advisory: GHSA-m8fw-p3cr-6jqc
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-m8fw-p3cr-6jqc
Type: github-advisory

## Affected
- Packagist: `typo3/cms-rte-ckeditor` — affected >=9.5.0 <9.5.42
- Packagist: `typo3/cms-rte-ckeditor` — affected >=10.0.0 <10.4.39
- Packagist: `typo3/cms-rte-ckeditor` — affected >=11.0.0 <11.5.30

## Details
> ### CVSS: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C` (4.4) 

### Problem
The [WordCount](https://ckeditor.com/cke4/addon/wordcount) plugin ([`npm:ckeditor-wordcount-plugin`](https://www.npmjs.com/package/ckeditor-wordcount-plugin)) for CKEditor4 is vulnerable to cross-site scripting when switching to the source code mode. This plugin is enabled via the `Full.yaml` configuration present, but is not active in the default configuration.

In default scenarios, exploiting this vulnerability requires a valid backend user account. However, if custom plugins are used on the website frontend, which accept and reflect rich-text content submitted by users, no authentication is required.

### Solution
Update to TYPO3 versions 9.5.42 ELTS, 10.4.39 ELTS, 11.5.30 that fix the problem described above.

### Credits
Thanks to Sybille Peters who reported this issue, and to TYPO3 core & security team member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2023-004](https://typo3.org/security/advisory/typo3-core-sa-2023-004)
* https://github.com/w8tcha/CKEditor-WordCount-Plugin/security/advisories/GHSA-q9w4-w667-qqj4

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-m8fw-p3cr-6jqc
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2023-004

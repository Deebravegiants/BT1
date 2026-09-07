# [M] Yii2 Gii Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x87m-36g7-6mpw
CVE: CVE-2022-34297
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-10
Source: https://github.com/advisories/GHSA-x87m-36g7-6mpw
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-gii` — affected >=0

## Details
Some fields like Message Category (requires I18N enabled) in Model Generator, CRUD Generator or Form Generator, Author Name in Extension Generator, etc. are being cached without sanitisation of their contents when the Preview button is pressed. This leads to possibility of injecting malicious javascript in specified pages by placing it in said fields and caching it by pressing Preview button. On each consequent visit of specified pages malicious javascript will be loaded from server and executed in client's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34297
- https://gist.github.com/be4r/b5c48d97ef6726d3ee37f995ee5aac81
- https://github.com/yiisoft/yii2-gii
- https://www.yiiframework.com/doc/guide/2.0/en/start-gii

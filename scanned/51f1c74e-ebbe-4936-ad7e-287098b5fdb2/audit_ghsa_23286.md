# [M] SunHater KCFinder cross-site scripting (XSS) vulnerability in upload.php

## Summary
Severity: Medium
Advisory: GHSA-vwh5-78jc-hpjx
CVE: CVE-2019-14315
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vwh5-78jc-hpjx
Type: github-advisory

## Affected
- Packagist: `sunhater/kcfinder` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in upload.php in SunHater KCFinder 3.20-test1, 3.20-test2, 3.12, and earlier allows remote attackers to inject arbitrary web script or HTML via the CKEditorFuncNum parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14315
- https://github.com/sunhater/kcfinder/issues/180
- https://github.com/sunhater/kcfinder/pull/186
- https://github.com/sunhater/kcfinder

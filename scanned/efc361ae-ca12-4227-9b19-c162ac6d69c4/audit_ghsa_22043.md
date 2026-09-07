# [M] Yii Cross-site Scripting Framework vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4c64-w8fg-xcq2
CVE: CVE-2017-11516
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4c64-w8fg-xcq2
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-dev` — affected >=2.0.12 <2.0.13
- Packagist: `yiisoft/yii2` — affected >=2.0.12 <2.0.13

## Details
An XSS vulnerability exists in framework/views/errorHandler/exception.php in Yii Framework 2.0.12 affecting the exception screen when debug mode is enabled, because $exception->errorInfo is mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11516
- https://github.com/yiisoft/yii2/pull/14492
- https://github.com/yiisoft/yii2/pull/14492/files/feb4067de8a58f391a66e395192b0d83a8109b95
- https://github.com/yiisoft/yii2-framework

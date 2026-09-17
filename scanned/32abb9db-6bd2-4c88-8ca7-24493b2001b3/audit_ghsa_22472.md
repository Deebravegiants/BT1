# [C] Yii SQL injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-hhg2-g6h6-c266
CVE: CVE-2018-7269
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hhg2-g6h6-c266
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-dev` — affected >=0 <2.0.12.1
- Packagist: `yiisoft/yii2-dev` — affected >=2.0.13 <2.0.13.2
- Packagist: `yiisoft/yii2-dev` — affected >=2.0.14 <2.0.15

## Details
The findByCondition function in `framework/db/ActiveRecord.php` in Yii 2.x before 2.0.15 allows remote attackers to conduct SQL injection attacks via a findOne() or findAll() call, unless a developer recognizes an undocumented need to sanitize array input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7269
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2-dev/CVE-2018-7269.yaml
- https://github.com/yiisoft/yii2
- https://www.yiiframework.com/news/168/releasing-yii-2-0-15-and-database-extensions-with-security-fixes

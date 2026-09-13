# [C] Yii2 allows attackers to execute any local .php file via a relative path in the view parameter

## Summary
Severity: Critical
Advisory: GHSA-7cfq-72w2-24q4
CVE: CVE-2015-5467
CWE: CWE-22, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-7cfq-72w2-24q4
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=2.0.0 <2.0.5

## Details
web\ViewAction in Yii (aka Yii2) 2.x before 2.0.5 allows attackers to execute any local .php file via a relative path in the view parameeter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5467
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2-dev/CVE-2015-5467.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2/CVE-2015-5467.yaml
- https://github.com/yiisoft/yii2-framework
- https://www.yiiframework.com/news/87/yii-2-0-5-is-released-security-fix

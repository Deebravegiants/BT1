# [C] yii2-redis Potential Remote code execution

## Summary
Severity: Critical
Advisory: GHSA-4hx3-m8w5-g5qh
CVE: CVE-2018-8073
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4hx3-m8w5-g5qh
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-redis` — affected >=0 <2.0.8

## Details
Potential remote code execution in LUA context of the redis server via methods `yii\redis\ActiveRecord::findOne()` and `yii\redis\ActiveRecord::findAll()` in yiisoft/yii2-redis. Attackers could probably manipulate data on the redis server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8073
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2-redis/CVE-2018-8073.yaml
- https://github.com/yiisoft/yii2-redis
- https://www.yiiframework.com/news/168/releasing-yii-2-0-15-and-database-extensions-with-security-fixes
- http://www.yiiframework.com/news/168/releasing-yii-2-0-15-and-database-extensions-with-security-fixes

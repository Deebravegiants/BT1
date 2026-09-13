# [H] Yii Framework Code Injection

## Summary
Severity: High
Advisory: GHSA-m2p5-fwp2-qcw2
CVE: CVE-2018-8074
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m2p5-fwp2-qcw2
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-dev` — affected >=2.0.0 <2.0.15
- Packagist: `yiisoft/yii2-elasticsearch` — affected >=0 <2.0.5

## Details
Yii 2.x before 2.0.15 allows remote attackers to inject unintended search conditions via a variant of the CVE-2018-7269 attack in conjunction with the Elasticsearch extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8074
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2-elasticsearch/CVE-2018-8074.yaml
- https://github.com/yiisoft/yii2
- https://www.yiiframework.com/news/168/releasing-yii-2-0-15-and-database-extensions-with-security-fixes
- http://www.yiiframework.com/news/168/releasing-yii-2-0-15-and-database-extensions-with-security-fixes

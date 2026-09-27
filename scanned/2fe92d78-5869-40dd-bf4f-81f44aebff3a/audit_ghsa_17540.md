# [M] Yii 2 Redis may expose AUTH parameters in logs in case of connection failure

## Summary
Severity: Medium
Advisory: GHSA-g3p6-82vc-43jh
CVE: CVE-2025-48493
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:L/VA:L/SC:L/SI:L/SA:H (CVSS_V4)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-g3p6-82vc-43jh
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-redis` — affected >=0 <2.0.20

## Details
### Impact

On failing connection extension writes commands sequence to logs. AUTH parameters are written in plain text exposing username and password. That might be an issue if attacker has access to logs.

## References
- https://github.com/yiisoft/yii2-redis/security/advisories/GHSA-g3p6-82vc-43jh
- https://nvd.nist.gov/vuln/detail/CVE-2025-48493
- https://github.com/yiisoft/yii2-redis/commit/962252d2c57c187181e67bb66da3f27b4698358d
- https://github.com/yiisoft/yii2-redis

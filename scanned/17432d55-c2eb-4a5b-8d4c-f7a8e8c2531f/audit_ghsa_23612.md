# [H] Yii Framework reflected Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-8gfq-c54m-3rf6
CVE: CVE-2018-6010
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8gfq-c54m-3rf6
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=2.0.0 <2.0.14

## Details
In Yii Framework 2.x before 2.0.14, remote attackers could obtain potentially sensitive information from exception messages, or exploit reflected XSS on the error handler page in non-debug mode. Related to base/ErrorHandler.php, log/Dispatcher.php, and views/errorHandler/exception.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6010
- https://github.com/yiisoft/yii2/issues/14711
- https://github.com/yiisoft/yii2/pull/15534
- https://github.com/yiisoft/yii2/commit/6b0be47e0fa9c532e03b07b4369050582fcf5c7a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2/CVE-2018-6010.yaml
- https://github.com/yiisoft/yii2-framework
- https://www.yiiframework.com/news/165/yii-2-0-14-is-released

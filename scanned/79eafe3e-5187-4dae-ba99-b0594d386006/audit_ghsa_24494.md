# [H] Yii Framework Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-cwhm-272p-3wj9
CVE: CVE-2018-6009
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cwhm-272p-3wj9
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=2.0 <2.0.14
- Packagist: `yiisoft/yii2-dev` — affected >=2.0 <2.0.14

## Details
In Yii Framework 2.x before 2.0.14, the switchIdentity function in web/User.php did not regenerate the CSRF token upon a change of identity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6009
- https://github.com/yiisoft/yii2/commit/6c0540aa2d6e0fe0fa89e4fd35bba4be5d6cece7
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2-dev/CVE-2018-6009.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2/CVE-2018-6009.yaml
- https://github.com/yiisoft/yii2-framework
- https://www.yiiframework.com/news/165/yii-2-0-14-is-released

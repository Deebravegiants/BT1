# [M] Yii Framework Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-4xh9-5vh8-3p58
CVE: CVE-2017-7271
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4xh9-5vh8-3p58
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=0 <2.0.11

## Details
Reflected Cross-site scripting (XSS) vulnerability in Yii Framework before 2.0.11, when development mode is used, allows remote attackers to inject arbitrary web script or HTML via crafted request data that is mishandled on the debug-mode exception screen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7271
- https://github.com/yiisoft/yii2/pull/13401
- https://github.com/yiisoft/yii2/commit/97171a0db7cda0a49931ee0c3b998ef50bd06756
- https://github.com/yiisoft/yii2
- https://web.archive.org/web/20210125191138/http://www.securityfocus.com/bid/97167
- http://www.yiiframework.com/news/123/yii-2-0-11-is-released

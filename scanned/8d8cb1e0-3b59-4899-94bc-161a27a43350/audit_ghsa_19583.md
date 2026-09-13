# [C] yiisoft/yii2 Mishandles the Attaching of Behavior Defined by a `__class` Array Key

## Summary
Severity: Critical
Advisory: GHSA-ggwg-cmwp-46r5
CVE: CVE-2024-58136
CWE: CWE-424
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-ggwg-cmwp-46r5
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=0 <2.0.52

## Details
Yii 2 before 2.0.52 mishandles the attaching of behavior that is defined by an __class array key, a CVE-2024-4990 regression, as exploited in the wild in February through April 2025.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-58136
- https://github.com/yiisoft/yii2/pull/20232
- https://github.com/yiisoft/yii2/pull/20232#issuecomment-2252459709
- https://github.com/yiisoft/yii2/commit/40fe496eda529fd1d933b56a1022ec32d3cd0b12
- https://github.com/yiisoft/yii2
- https://github.com/yiisoft/yii2/compare/2.0.51...2.0.52
- https://sensepost.com/blog/2025/investigating-an-in-the-wild-campaign-using-rce-in-craftcms
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-58136
- https://www.yiiframework.com/news/709/please-upgrade-to-yii-2-0-52

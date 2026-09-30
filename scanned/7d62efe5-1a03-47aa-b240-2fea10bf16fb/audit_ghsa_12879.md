# [H] Command injection in yiisoft/yii2-gii

## Summary
Severity: High
Advisory: GHSA-3mpg-q26j-83j5
CVE: CVE-2020-36655
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-21
Source: https://github.com/advisories/GHSA-3mpg-q26j-83j5
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-gii` — affected >=0 <2.2.2

## Details
Yii Yii2 Gii before 2.2.2 allows remote attackers to execute arbitrary code via the Generator.php messageCategory field. The attacker can embed arbitrary PHP code into the model file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36655
- https://github.com/yiisoft/yii2-gii/issues/433
- https://github.com/yiisoft/yii2-gii/commit/ed61e0d85f43e23f79d7c9d1b4e5e5c09a32ce4b
- https://github.com/yiisoft/yii2-gii
- https://lab.wallarm.com/yii2-gii-remote-code-execution

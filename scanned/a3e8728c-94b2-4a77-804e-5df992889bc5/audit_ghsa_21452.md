# [H] Prevent RCE when deserializing untrusted user input

## Summary
Severity: High
Advisory: GHSA-442f-wcwq-fpcf
CVE: CVE-2022-41922
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-442f-wcwq-fpcf
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii` — affected >=0 <1.1.27

## Details
### Impact
Affected versions of `yiisoft/yii` are vulnerable to Remote Code Execution (RCE) if the application calls `unserialize()` on arbitrary user input.

### Patches
Upgrade `yiisoft/yii` to version 1.1.27 or higher.

### For more information
See the following links for more details:
- [Git commit](https://github.com/yiisoft/yii/commit/ed67b7cc57216557c5c595c6650cdd2d3aa41c52)
- https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection

If you have any questions or comments about this advisory, [contact us through security form](https://www.yiiframework.com/security).

## References
- https://github.com/yiisoft/yii/security/advisories/GHSA-442f-wcwq-fpcf
- https://nvd.nist.gov/vuln/detail/CVE-2022-41922
- https://github.com/yiisoft/yii/commit/ed67b7cc57216557c5c595c6650cdd2d3aa41c52
- https://github.com/yiisoft/yii

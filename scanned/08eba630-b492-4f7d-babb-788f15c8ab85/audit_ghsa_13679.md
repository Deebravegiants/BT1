# [H] yiisoft/yii deserializing untrusted user input can lead to remote code execution

## Summary
Severity: High
Advisory: GHSA-mw2w-2hj2-fg8q
CVE: CVE-2023-47130
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-mw2w-2hj2-fg8q
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii` — affected >=0 <1.1.29

## Details
### Impact
Affected versions of `yiisoft/yii` are vulnerable to Remote Code Execution (RCE) if the application calls `unserialize()` on arbitrary user input.

### Patches
Upgrade `yiisoft/yii` to version 1.1.29 or higher.

### For more information
See the following links for more details:
- [Git commit](https://github.com/yiisoft/yii/commit/37142be4dc5831114a375392e86d6450d4951c06)
- https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection

If you have any questions or comments about this advisory, [contact us through security form](https://www.yiiframework.com/security).

## References
- https://github.com/yiisoft/yii/security/advisories/GHSA-mw2w-2hj2-fg8q
- https://nvd.nist.gov/vuln/detail/CVE-2023-47130
- https://github.com/yiisoft/yii/commit/37142be4dc5831114a375392e86d6450d4951c06
- https://github.com/yiisoft/yii
- https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection

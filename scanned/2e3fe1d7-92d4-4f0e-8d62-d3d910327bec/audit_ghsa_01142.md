# [H] Unsafe deserialization in Yii 2

## Summary
Severity: High
Advisory: GHSA-699q-wcff-g9mj
CVE: CVE-2020-15148
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2020-09-15
Source: https://github.com/advisories/GHSA-699q-wcff-g9mj
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=0 <2.0.38

## Details
### Impact

Remote code execution in case application calls `unserialize()` on user input containing specially crafted string.

### Patches

2.0.38

### Workarounds

Add the following to BatchQueryResult.php:

```php
public function __sleep()
{
    throw new \BadMethodCallException('Cannot serialize '.__CLASS__);
}

public function __wakeup()
{
    throw new \BadMethodCallException('Cannot unserialize '.__CLASS__);
}
```

### For more information

If you have any questions or comments about this advisory, [contact us through security form](https://www.yiiframework.com/security).

## References
- https://github.com/yiisoft/yii2/security/advisories/GHSA-699q-wcff-g9mj
- https://nvd.nist.gov/vuln/detail/CVE-2020-15148
- https://github.com/yiisoft/yii2/commit/9abccb96d7c5ddb569f92d1a748f50ee9b3e2b99
- https://github.com/FriendsOfPHP/security-advisories/blob/master/yiisoft/yii2/CVE-2020-15148.yaml
- https://www.yiiframework.com/news/303/yii-2-0-38

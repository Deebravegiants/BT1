# [M] Yii does not prevent XSS in scenarios where fallback error renderer is used

## Summary
Severity: Medium
Advisory: GHSA-7r2v-8wxr-3ch5
CVE: CVE-2025-32027
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-7r2v-8wxr-3ch5
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii` — affected >=0 <1.1.31

## Details
### Impact
Affected versions of yiisoft/yii are vulnerable to Reflected XSS in specific scenarios where the fallback error renderer is used.

### Patches
Upgrade yiisoft/yii to version 1.1.31 or higher.

### References
- [Git commit](https://github.com/yiisoft/yii/commit/d386d737861c9014269b7ed8c36c65eadb387368)

If you have any questions or comments about this advisory, [contact us through security form](https://www.yiiframework.com/security).

## References
- https://github.com/yiisoft/yii/security/advisories/GHSA-7r2v-8wxr-3ch5
- https://nvd.nist.gov/vuln/detail/CVE-2025-32027
- https://github.com/yiisoft/yii/commit/d386d737861c9014269b7ed8c36c65eadb387368
- https://github.com/yiisoft/yii

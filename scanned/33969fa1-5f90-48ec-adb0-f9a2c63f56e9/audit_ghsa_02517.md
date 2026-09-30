# [H] Improperly Controlled Modification of Object Prototype Attributes

## Summary
Severity: High
Advisory: GHSA-6cj2-92m5-7mvp
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-03
Source: https://github.com/advisories/GHSA-6cj2-92m5-7mvp
Type: github-advisory

## Affected
- npm: `think-config` — affected >=0 <1.1.3

## Details
### Impact

The software receives input from an upstream component that specifies attributes that are to be initialized or updated in an object, but it does not properly control modifications of attributes of the object prototype.

### Patches

`think-config@1.1.3` patched it, anyone used `think-config` should upgrade to `>=1.1.3` version.

### References

https://cwe.mitre.org/data/definitions/1321.html

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [thinkjs/thinkjs](https://github.com/thinkjs/thinkjs)
* Email us at [i@imnerd.org](mailto:i@imnerd.org)

## References
- https://github.com/thinkjs/think-config/security/advisories/GHSA-6cj2-92m5-7mvp
- https://github.com/thinkjs/think-config

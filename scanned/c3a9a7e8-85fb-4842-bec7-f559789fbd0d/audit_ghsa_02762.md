# [H] Prototype Pollution in think-helper

## Summary
Severity: High
Advisory: GHSA-vr5m-3h59-7jcp
CVE: CVE-2021-32736
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-vr5m-3h59-7jcp
Type: github-advisory

## Affected
- npm: `think-helper` — affected >=0 <1.1.3

## Details
### Impact

The software receives input from an upstream component that specifies attributes that are to be initialized or updated in an object, but it does not properly control modifications of attributes of the object prototype.

### Patches

`think-helper@1.1.3` patched it, anyone used `think-helper` should upgrade to `>=1.1.3` version.

### References

https://cwe.mitre.org/data/definitions/1321.html

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [thinkjs/thinkjs](https://github.com/thinkjs/thinkjs)
* Email us at [i@imnerd.org](mailto:i@imnerd.org)

## References
- https://github.com/thinkjs/think-helper/security/advisories/GHSA-vr5m-3h59-7jcp
- https://nvd.nist.gov/vuln/detail/CVE-2021-32736
- https://github.com/thinkjs/think-helper

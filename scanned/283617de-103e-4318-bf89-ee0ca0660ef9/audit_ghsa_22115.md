# [H] Reversible One-Way Hash in io.github.javaezlib:JavaEZ

## Summary
Severity: High
Advisory: GHSA-67fj-6w6m-w5j8
CVE: CVE-2022-29249
CWE: CWE-326, CWE-327, CWE-328
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-67fj-6w6m-w5j8
Type: github-advisory

## Affected
- Maven: `io.github.javaezlib:JavaEZ` — affected >=1.6 <1.7

## Details
### Impact
This weakness allows the force decryption of locked text by hackers. The issue is NOT critical for non-secure applications, however may be critical in a situation where the highest levels of security are required. This issue ONLY affects v1.6 and does not affect anything pre-1.6. Upgrading to 1.7 is advised.

### Patches
The vulnerability has been patched in release 1.7.

### Workarounds
Currently there is no way to fix the issue without upgrading.

### References
[CWE-327](https://cwe.mitre.org/data/definitions/327.html)
[CWE-328](https://cwe.mitre.org/data/definitions/328.html)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](http://github.com/JavaEZLib/JavaEZ/issues)
* Email us at [javaezlib@gmail.com](mailto:javaezlib@gmail.com)

## References
- https://github.com/JavaEZLib/JavaEZ/security/advisories/GHSA-67fj-6w6m-w5j8
- https://nvd.nist.gov/vuln/detail/CVE-2022-29249
- https://github.com/JavaEZLib/JavaEZ
- https://github.com/JavaEZLib/JavaEZ/releases/tag/1.7

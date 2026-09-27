# [H] untangle vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-f83q-2cp7-qrjg
CVE: CVE-2022-31471
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-f83q-2cp7-qrjg
Type: github-advisory

## Affected
- PyPI: `untangle` — affected >=0 <1.2.1

## Details
### Description
untangle is a python library to convert XML data to python objects. untangle versions 1.2.0 and earlier improperly restricts XML external entity references. By exploiting this vulnerability, a remote unauthenticated attacker may read the contents of local files.

### Impact
An attacker may be able to read the contents of local files. This affects untangle versions up to and including 1.2.0

### Patches
The problem has been fixed with version 1.2.1

### Workarounds
None

### References
https://jvn.jp/en/jp/JVN30454777/

### For more information
If you have any questions or comments about this advisory:
* Open an [issue](https://github.com/stchris/untangle/issues)

## References
- https://github.com/stchris/untangle/security/advisories/GHSA-f83q-2cp7-qrjg
- https://nvd.nist.gov/vuln/detail/CVE-2022-31471
- https://github.com/pypa/advisory-database/tree/main/vulns/untangle/PYSEC-2022-244.yaml
- https://github.com/stchris/untangle
- https://github.com/stchris/untangle/releases/tag/1.2.1
- https://jvn.jp/en/jp/JVN30454777

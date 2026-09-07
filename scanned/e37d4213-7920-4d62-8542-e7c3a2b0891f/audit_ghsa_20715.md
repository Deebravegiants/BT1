# [H] untangle vulnerable to XML Entity Expansion

## Summary
Severity: High
Advisory: GHSA-7xr3-6ggc-wc9p
CVE: CVE-2022-33977
CWE: CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-7xr3-6ggc-wc9p
Type: github-advisory

## Affected
- PyPI: `untangle` — affected >=0 <1.2.1

## Details
### Impact
An attacker may be able to cause a denial-of-service (DoS) condition on the server on which the product is running. This affects untangle versions up to and including 1.2.0

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
- https://github.com/stchris/untangle/security/advisories/GHSA-7xr3-6ggc-wc9p
- https://nvd.nist.gov/vuln/detail/CVE-2022-33977
- https://github.com/pypa/advisory-database/tree/main/vulns/untangle/PYSEC-2022-243.yaml
- https://github.com/stchris/untangle
- https://github.com/stchris/untangle/releases/tag/1.2.1
- https://jvn.jp/en/jp/JVN30454777

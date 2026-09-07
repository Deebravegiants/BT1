# [M] Cross-site Scripting in Weblate

## Summary
Severity: Medium
Advisory: GHSA-6jp6-9rf9-gc66
CVE: CVE-2022-24710
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-6jp6-9rf9-gc66
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <4.11

## Details
### Impact
Due to improper neutralization, it was possible to perform cross-site scripting via crafted user and language names.

### Patches

The issues were fixed in the 4.11 release. The following commits are addressing it:

* f6753a1a1c63fade6ad418fbda827c6750ab0bda
* 9e19a8414337692cc90da2a91c9af5420f2952f1
* 22d577b1f1e88665a88b4569380148030e0f8389

### Workarounds

You can look for crafted user and language names to see if you were affected.

### References
* https://hackerone.com/reports/1486674
* https://hackerone.com/reports/1486718
* https://hackerone.com/reports/1485226

### For more information
If you have any questions or comments about this advisory:
* Open a topic in [discussions](https://github.com/WeblateOrg/weblate/discussions)
* Email us at [care@weblate.org](mailto:care@weblate.org)

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-6jp6-9rf9-gc66
- https://nvd.nist.gov/vuln/detail/CVE-2022-24710
- https://github.com/WeblateOrg/weblate/commit/22d577b1f1e88665a88b4569380148030e0f8389
- https://github.com/WeblateOrg/weblate/commit/9e19a8414337692cc90da2a91c9af5420f2952f1
- https://github.com/WeblateOrg/weblate/commit/f6753a1a1c63fade6ad418fbda827c6750ab0bda
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2022-35.yaml

# [M] collective.dms.basecontent Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r48c-4vfj-h426
CVE: CVE-2022-4495
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-r48c-4vfj-h426
Type: github-advisory

## Affected
- PyPI: `collective.dms.basecontent` — affected >=0 <1.7

## Details
A vulnerability, which was classified as problematic, has been found in collective.dms.basecontent. This issue affects the function renderCell of the file src/collective/dms/basecontent/browser/column.py. The manipulation leads to cross site scripting. The attack may be initiated remotely. Upgrading to version 1.7 or later will address this issue. The patch is at commit 6c4d616fcc771822a14ebae5e23f3f6d96d134bd. It is recommended to upgrade the affected component. The identifier VDB-215813 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4495
- https://github.com/collective/collective.dms.basecontent/commit/6c4d616fcc771822a14ebae5e23f3f6d96d134bd
- https://github.com/collective/collective.dms.basecontent
- https://github.com/collective/collective.dms.basecontent/releases/tag/1.7
- https://github.com/pypa/advisory-database/tree/main/vulns/collective-dms-basecontent/PYSEC-2022-42989.yaml
- https://vuldb.com/?id.215813

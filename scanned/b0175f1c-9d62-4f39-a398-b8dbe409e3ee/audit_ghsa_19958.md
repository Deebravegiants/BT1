# [M] collective.task Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4r9h-x77w-mffv
CVE: CVE-2022-4527
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-4r9h-x77w-mffv
Type: github-advisory

## Affected
- PyPI: `collective.task` — affected >=0 <3.0.9

## Details
A vulnerability was found in collective.task up to 3.0.9. It has been classified as problematic. This affects the function renderCell/AssignedGroupColumn of the file src/collective/task/browser/table.py. The manipulation leads to cross site scripting. It is possible to initiate the attack remotely. Upgrading to version 3.0.10 is able to address this issue. The name of the patch is 1aac7f83fa2c2b41d59ba02748912953461f3fac. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-215907.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4527
- https://github.com/collective/collective.task/commit/1aac7f83fa2c2b41d59ba02748912953461f3fac
- https://github.com/collective/collective.task
- https://github.com/collective/collective.task/releases/tag/3.0.10
- https://github.com/collective/collective.task/releases/tag/3.0.9
- https://github.com/pypa/advisory-database/tree/main/vulns/collective-task/PYSEC-2022-42990.yaml
- https://vuldb.com/?id.215907

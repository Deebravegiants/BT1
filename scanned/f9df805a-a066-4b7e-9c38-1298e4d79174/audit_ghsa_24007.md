# [M] MantisBT Incorrect Authorization in bug_actiongroup_page.php

## Summary
Severity: Medium
Advisory: GHSA-pgg9-mmcg-8mxp
CVE: CVE-2020-29605
CWE: CWE-863
Ecosystem: Packagist
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pgg9-mmcg-8mxp
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.4

## Details
An issue was discovered in MantisBT before 2.24.4. Due to insufficient access-level checks, any logged-in user allowed to perform Group Actions can get access to the Summary fields of private Issues via bug_arr[]= in a crafted bug_actiongroup_page.php URL. (The target Issues can have Private view status, or belong to a private Project.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29605
- https://github.com/mantisbt/mantisbt/commit/9322c8c9f57fb72f3b8b033889a6a09c441d5be0
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27357
- https://mantisbt.org/bugs/view.php?id=27727

# [M] MantisBT Missing Authorization access check in bug_actiongroup.php

## Summary
Severity: Medium
Advisory: GHSA-f38c-wxp6-8xjv
CVE: CVE-2020-29604
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f38c-wxp6-8xjv
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.4

## Details
An issue was discovered in MantisBT before 2.24.4. A missing access check in bug_actiongroup.php allows an attacker (with rights to create new issues) to use the COPY group action to create a clone, including all bugnotes and attachments, of any private issue (i.e., one having Private view status, or belonging to a private Project) via the bug_arr[] parameter. This provides full access to potentially confidential information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29604
- https://github.com/mantisbt/mantisbt/commit/b2da7352b0ad31fa5f925eaacb4b2b96a6cec8e8
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27357
- https://mantisbt.org/bugs/view.php?id=27728

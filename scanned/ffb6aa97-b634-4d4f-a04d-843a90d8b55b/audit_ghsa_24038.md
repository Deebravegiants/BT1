# [M] MantisBT Insecure Storage in manage_proj_edit_page.php

## Summary
Severity: Medium
Advisory: GHSA-qpj5-f88q-x7px
CVE: CVE-2020-29603
CWE: CWE-922
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qpj5-f88q-x7px
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.4

## Details
In manage_proj_edit_page.php in MantisBT before 2.24.4, any unprivileged logged-in user can retrieve Private Projects' names via the manage_proj_edit_page.php project_id parameter, without having access to them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29603
- https://github.com/mantisbt/mantisbt/commit/cff10f266f67e2da3060ea4d0b9ecbb29c21b869
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27357
- https://mantisbt.org/bugs/view.php?id=27726

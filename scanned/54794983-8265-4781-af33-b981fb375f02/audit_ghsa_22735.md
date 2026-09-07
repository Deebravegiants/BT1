# [M] MantisBT XXS where a Custom Field with a crafted Regular Expression property is used

## Summary
Severity: Medium
Advisory: GHSA-qgrr-f26j-87vf
CVE: CVE-2020-25288
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qgrr-f26j-87vf
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.23.0 <2.24.3

## Details
An issue was discovered in MantisBT before 2.24.3. When editing an Issue in a Project where a Custom Field with a crafted Regular Expression property is used, improper escaping of the corresponding form input's pattern attribute allows HTML injection and, if CSP settings permit, execution of arbitrary JavaScript.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25288
- https://github.com/mantisbt/mantisbt/commit/221cf323f16a9738a5b27aaba94758f11281d85c
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27275
- http://github.com/mantisbt/mantisbt/commit/221cf323f16a9738a5b27aaba94758f11281d85c

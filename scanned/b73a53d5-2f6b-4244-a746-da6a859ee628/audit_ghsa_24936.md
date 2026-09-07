# [M] MantisBT HTML Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2pm7-q8pc-xhvq
CVE: CVE-2020-25830
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2pm7-q8pc-xhvq
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.3

## Details
An issue was discovered in MantisBT before 2.24.3. Improper escaping of a custom field's name allows an attacker to inject HTML and, if CSP settings permit, achieve execution of arbitrary JavaScript when attempting to update said custom field via `bug_actiongroup_page.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25830
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27304
- http://github.com/mantisbt/mantisbt/commit/8c6f4d8859785b67fb80ac65100ac5259ed9237d

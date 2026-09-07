# [M] MantisBT allows XSS in manage_custom_field_edit_page.php

## Summary
Severity: Medium
Advisory: GHSA-52cx-vphc-jmjm
CVE: CVE-2021-33557
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-52cx-vphc-jmjm
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.25.2

## Details
An XSS issue was discovered in manage_custom_field_edit_page.php in MantisBT before 2.25.2. Unescaped output of the return parameter allows an attacker to inject code into a hidden input field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33557
- https://github.com/mantisbt/mantisbt/commit/03dd37221e636f8959b8cb9fbad84f38f9582356
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/blog/archives/mantisbt/699
- https://mantisbt.org/bugs/view.php?id=28552

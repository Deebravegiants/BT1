# [M] MantisBT vulnerable to XSS via unsanitized filter field in manage_user_page.php

## Summary
Severity: Medium
Advisory: GHSA-w93w-rx52-24qh
CVE: CVE-2017-12062
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w93w-rx52-24qh
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.0.0 <2.5.2

## Details
An XSS issue was discovered in manage_user_page.php in MantisBT 2.x before 2.5.2. The 'filter' field is not sanitized before being rendered in the Manage User page, allowing remote attackers to execute arbitrary JavaScript code if CSP is disabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12062
- https://github.com/mantisbt/mantisbt/commit/9b5b71dadbeeeec27efea59f562ac5bd6d2673b7
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=23166
- http://openwall.com/lists/oss-security/2017/08/01/1
- http://openwall.com/lists/oss-security/2017/08/01/2

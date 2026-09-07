# [M] MantisBT XSS via my_view_page.php and view_user_page.php

## Summary
Severity: Medium
Advisory: GHSA-8r2m-qhff-jm2c
CVE: CVE-2017-7897
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8r2m-qhff-jm2c
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.3.0 <2.3.2

## Details
A cross-site scripting (XSS) vulnerability in the MantisBT (2.3.x before 2.3.2) Timeline include page, used in My View (my_view_page.php) and User Information (view_user_page.php) pages, allows remote attackers to inject arbitrary code (if CSP settings permit it) through crafted PATH_INFO in a URL, due to use of unsanitized $_SERVER['PHP_SELF'] to generate URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7897
- https://github.com/mantisbt/mantisbt/pull/1094
- https://github.com/mantisbt/mantisbt/commit/a1c719313d61b07bbe8700005807b8195fdc32f1
- https://github.com/mantisbt/mantisbt
- http://www.mantisbt.org/bugs/view.php?id=22742

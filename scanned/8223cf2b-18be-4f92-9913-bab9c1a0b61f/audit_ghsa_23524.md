# [M] MantisBT allows XSS via View Filters page 

## Summary
Severity: Medium
Advisory: GHSA-mjp7-97w4-jwhc
CVE: CVE-2018-13055
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mjp7-97w4-jwhc
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.1.0 <2.15.1

## Details
A cross-site scripting (XSS) vulnerability in the View Filters page (view_filters_page.php) in MantisBT 2.1.0 through 2.15.0 allows remote attackers to inject arbitrary code (if CSP settings permit it) through a crafted PATH_INFO.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13055
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/blog/archives/mantisbt/602
- https://mantisbt.org/bugs/view.php?id=24580
- http://github.com/mantisbt/mantisbt/commit/4efac90ed89a5c009108b641e2e95683791a165a

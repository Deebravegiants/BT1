# [M] MantisBT allows XSS via the Manage Filter page 

## Summary
Severity: Medium
Advisory: GHSA-ggjm-7m5f-7xjv
CVE: CVE-2018-17782
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-ggjm-7m5f-7xjv
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.1.0 <2.17.2

## Details
A cross-site scripting (XSS) vulnerability in the Manage Filters page (manage_filter_page.php) in MantisBT 2.1.0 through 2.17.1 allows remote attackers (if access rights permit it) to inject arbitrary code (if CSP settings permit it) through a crafted project name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17782
- https://github.com/mantisbt/mantisbt/commit/72ab020a42a35fd341e983a25849f8277bb34044
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/blog/archives/mantisbt/613
- https://mantisbt.org/bugs/view.php?id=24813

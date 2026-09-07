# [M] MantisBT cross-site scripting (XSS) vulnerability through crafted PATH_INFO

## Summary
Severity: Medium
Advisory: GHSA-3qv7-98vm-xx2v
CVE: CVE-2018-16514
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3qv7-98vm-xx2v
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.1.0 <2.17.1

## Details
A cross-site scripting (XSS) vulnerability in the View Filters page (view_filters_page.php) and Edit Filter page (manage_filter_edit_page.php) in MantisBT 2.1.0 through 2.17.0 allows remote attackers to inject arbitrary code (if CSP settings permit it) through a crafted PATH_INFO. NOTE: this vulnerability exists because of an incomplete fix for CVE-2018-13055.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16514
- https://github.com/mantisbt/mantisbt/commit/66091a42626631a3063774eb0fb8a4218ab22fd4
- https://github.com/mantisbt/mantisbt
- https://github.com/mantisbt/mantisbt/blob/006cd0cd90c37097e1a065fd3e59ce2534490834/core/filter_form_api.php#L2779
- https://mantisbt.org/bugs/view.php?id=24731

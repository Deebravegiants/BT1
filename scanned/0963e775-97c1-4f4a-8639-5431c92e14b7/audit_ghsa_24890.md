# [M] MantisBT allows cross-site scripting (XSS) via crafted filename

## Summary
Severity: Medium
Advisory: GHSA-gg4j-279j-22ph
CVE: CVE-2019-15074
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gg4j-279j-22ph
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.21.2

## Details
The Timeline feature in my_view_page.php in MantisBT through 2.21.1 has a stored cross-site scripting (XSS) vulnerability, allowing execution of arbitrary code (if CSP settings permit it) after uploading an attachment with a crafted filename. The code is executed for any user having visibility to the issue, whenever My View Page is displayed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15074
- https://github.com/mantisbt/mantisbt/commit/9cee1971c498bbe0a72bca1c773fae50171d8c27
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=25995

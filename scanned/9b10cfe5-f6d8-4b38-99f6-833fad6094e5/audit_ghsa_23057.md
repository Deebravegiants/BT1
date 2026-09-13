# [C] NukeViet SQL Injection vulnerability via topicsid parameter

## Summary
Severity: Critical
Advisory: GHSA-84gf-rw24-pfqg
CVE: CVE-2020-21808
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-84gf-rw24-pfqg
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=4.0.10 <4.3.08

## Details
SQL Injection vulnerability in NukeViet CMS 4.0.10 - 4.3.07 via the topicsid parameter in `modules/news/admin/addtotopics.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21808
- https://github.com/nukeviet/nukeviet
- https://github.com/nukeviet/nukeviet/blob/4.3.08/CHANGELOG.txt#L11
- https://nukeviet.vn/vi/news/Tin-an-ninh/huong-dan-fix-loi-bao-mat-nukeviet-4-va-module-shops-612.html
- https://whitehub.net/submissions/1516

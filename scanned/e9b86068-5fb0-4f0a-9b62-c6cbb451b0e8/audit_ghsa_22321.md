# [H] NukeViet Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-7rw5-6pr4-fgh3
CVE: CVE-2020-13155
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7rw5-6pr4-fgh3
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected 4.4.0

## Details
`clearsystem.php` in NukeViet 4.4 allows CSRF with resultant HTML injection via the deltype parameter to the `admin/index.php?nv=webtools&op=clearsystem` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13155
- https://github.com/nukeviet/nukeviet
- https://nukeviet.vn/en
- https://www.exploit-db.com/exploits/48489

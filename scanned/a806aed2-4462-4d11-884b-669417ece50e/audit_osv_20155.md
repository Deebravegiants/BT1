# [M] CVE-2021-31731

## Summary
Severity: Medium
Advisory: CVE-2021-31731
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-31731
Type: osv

## Details
A directory traversal issue in KiteCMS 1.1.1 allows remote administrators to overwrite arbitrary files via ../ in the path parameter to index.php/admin/Template/fileedit, with PHP code in the html parameter.

## References
- https://github.com/Kitesky/KiteCMS/issues/9

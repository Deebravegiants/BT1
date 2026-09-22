# [M] CVE-2020-35709

## Summary
Severity: Medium
Advisory: CVE-2020-35709
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-12-25
Source: https://osv.dev/vulnerability/CVE-2020-35709
Type: osv

## Details
bloofoxCMS 0.5.2.1 allows admins to upload arbitrary .php files (with "Content-Type: application/octet-stream") to ../media/images/ via the admin/index.php?mode=tools&page=upload URI, aka directory traversal.

## References
- https://github.com/alexlang24/bloofoxCMS/issues/7

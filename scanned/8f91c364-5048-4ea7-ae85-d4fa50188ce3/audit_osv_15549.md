# [M] CVE-2019-17073

## Summary
Severity: Medium
Advisory: CVE-2019-17073
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-10-01
Source: https://osv.dev/vulnerability/CVE-2019-17073
Type: osv

## Details
emlog through 6.0.0beta allows remote authenticated users to delete arbitrary files via admin/template.php?action=del&tpl=../ directory traversal.

## References
- https://github.com/emlog/emlog/issues/49

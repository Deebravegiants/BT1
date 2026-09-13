# [M] CVE-2019-12309

## Summary
Severity: Medium
Advisory: CVE-2019-12309
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2019-12309
Type: osv

## Details
dotCMS before 5.1.0 has a path traversal vulnerability exploitable by an administrator to create files. The vulnerability is caused by the insecure extraction of a ZIP archive.

## References
- https://dotcms.com/security/SI-48
- https://github.com/dotCMS/core/compare/605e5db...364c910

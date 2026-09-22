# [H] CVE-2019-12548

## Summary
Severity: High
Advisory: CVE-2019-12548
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-12548
Type: osv

## Details
Bludit before 3.9.0 allows remote code execution for an authenticated user by uploading a php file while changing the logo through /admin/ajax/upload-logo.

## References
- https://github.com/bludit/bludit/compare/5e5957c...77e85e7
- https://github.com/bludit/bludit/releases/tag/3.9.0
- https://github.com/bludit/bludit/commit/d0843a4070c7d7fa596a7eb2130be15383013487

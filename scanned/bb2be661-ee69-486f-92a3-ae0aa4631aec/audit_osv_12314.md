# [C] CVE-2018-11331

## Summary
Severity: Critical
Advisory: CVE-2018-11331
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-21
Source: https://osv.dev/vulnerability/CVE-2018-11331
Type: osv

## Details
An issue was discovered in Pluck before 4.7.6. Remote PHP code execution is possible because the set of disallowed filetypes for uploads in missing some applicable ones such as .phtml and .htaccess.

## References
- https://github.com/pluck-cms/pluck/commit/8f6541e60c9435e82e9c531a20cb3c218d36976e
- https://github.com/pluck-cms/pluck/issues/58

# [H] CVE-2019-12742

## Summary
Severity: High
Advisory: CVE-2019-12742
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-12742
Type: osv

## Details
Bludit prior to 3.9.1 allows a non-privileged user to change the password of any account, including admin. This occurs because of bl-kernel/admin/controllers/user-password.php Insecure Direct Object Reference (a modified username POST parameter).

## References
- https://github.com/bludit/bludit/releases/tag/3.9.1
- https://github.com/bludit/bludit/commit/a1bb333153fa8ba29a88cfba423d810f509a2b37

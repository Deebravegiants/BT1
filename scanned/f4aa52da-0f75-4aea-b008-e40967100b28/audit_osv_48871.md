# [H] CVE-2018-16744

## Summary
Severity: High
Advisory: CVE-2018-16744
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-13
Source: https://osv.dev/vulnerability/CVE-2018-16744
Type: osv

## Details
An issue was discovered in mgetty before 1.2.1. In fax_notify_mail() in faxrec.c, the mail_to parameter is not sanitized. It could allow for command injection if untrusted input can reach it, because popen is used.

## References
- https://www.x41-dsec.de/lab/advisories/x41-2018-007-mgetty

# [H] CVE-2018-16741

## Summary
Severity: High
Advisory: CVE-2018-16741
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-13
Source: https://osv.dev/vulnerability/CVE-2018-16741
Type: osv

## Details
An issue was discovered in mgetty before 1.2.1. In fax/faxq-helper.c, the function do_activate() does not properly sanitize shell metacharacters to prevent command injection. It is possible to use the ||, &&, or > characters within a file created by the "faxq-helper activate <jobid>" command.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00012.html
- https://www.debian.org/security/2018/dsa-4291
- https://www.x41-dsec.de/lab/advisories/x41-2018-007-mgetty

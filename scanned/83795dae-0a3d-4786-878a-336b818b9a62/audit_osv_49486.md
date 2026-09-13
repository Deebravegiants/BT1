# [C] CVE-2019-13485

## Summary
Severity: Critical
Advisory: CVE-2019-13485
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-27
Source: https://osv.dev/vulnerability/CVE-2019-13485
Type: osv

## Details
In Xymon through 4.3.28, a stack-based buffer overflow vulnerability exists in the history viewer component via a long hostname or service parameter to history.c.

## References
- https://github.com/svn2github/xymon/blob/master/branches/4.3.28/web/history.c
- https://lists.debian.org/debian-lts-announce/2019/08/msg00032.html
- https://lists.xymon.com/archive/2019-July/046570.html

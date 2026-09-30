# [H] CVE-2019-3461

## Summary
Severity: High
Advisory: CVE-2019-3461
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-3461
Type: osv

## Details
Debian tmpreaper version 1.6.13+nmu1 has a race condition when doing a (bind) mount via rename() which could result in local privilege escalation. Mounting via rename() could potentially lead to a file being placed elsewhereon the filesystem hierarchy (e.g. /etc/cron.d/) if the directory being cleaned up was on the same physical filesystem. Fixed versions include 1.6.13+nmu1+deb9u1 and 1.6.14.

## References
- https://usn.ubuntu.com/4077-1/
- https://lists.debian.org/debian-security-announce/2019/msg00003.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=918956
- https://lists.debian.org/debian-lts-announce/2019/01/msg00017.html

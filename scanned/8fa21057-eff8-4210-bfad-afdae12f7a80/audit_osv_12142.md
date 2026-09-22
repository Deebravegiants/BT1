# [M] CVE-2018-10545

## Summary
Severity: Medium
Advisory: CVE-2018-10545
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10545
Type: osv

## Details
An issue was discovered in PHP before 5.6.35, 7.0.x before 7.0.29, 7.1.x before 7.1.16, and 7.2.x before 7.2.4. Dumpable FPM child processes allow bypassing opcache access controls because fpm_unix.c makes a PR_SET_DUMPABLE prctl call, allowing one user (in a multiuser environment) to obtain sensitive information from the process memory of a second user's PHP applications by running gcore on the PID of the PHP-FPM worker process.

## References
- http://www.securityfocus.com/bid/104022
- https://access.redhat.com/errata/RHSA-2019:2519
- https://lists.debian.org/debian-lts-announce/2018/05/msg00004.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00005.html
- https://security.gentoo.org/glsa/201812-01
- https://security.netapp.com/advisory/ntap-20180607-0003/
- https://usn.ubuntu.com/3646-1/
- https://usn.ubuntu.com/3646-2/
- https://www.debian.org/security/2018/dsa-4240
- https://www.tenable.com/security/tns-2018-12
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=75605

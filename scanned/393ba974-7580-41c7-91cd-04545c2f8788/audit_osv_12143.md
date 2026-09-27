# [H] CVE-2018-10546

## Summary
Severity: High
Advisory: CVE-2018-10546
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10546
Type: osv

## Details
An issue was discovered in PHP before 5.6.36, 7.0.x before 7.0.30, 7.1.x before 7.1.17, and 7.2.x before 7.2.5. An infinite loop exists in ext/iconv/iconv.c because the iconv stream filter does not reject invalid multibyte sequences.

## References
- http://www.securityfocus.com/bid/104019
- http://www.securitytracker.com/id/1040807
- https://access.redhat.com/errata/RHSA-2019:2519
- https://lists.debian.org/debian-lts-announce/2018/06/msg00005.html
- https://security.gentoo.org/glsa/201812-01
- https://security.netapp.com/advisory/ntap-20180607-0003/
- https://usn.ubuntu.com/3646-1/
- https://www.debian.org/security/2018/dsa-4240
- https://www.tenable.com/security/tns-2018-12
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=76249

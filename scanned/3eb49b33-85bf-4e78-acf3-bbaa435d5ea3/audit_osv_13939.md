# [M] CVE-2018-5711

## Summary
Severity: Medium
Advisory: CVE-2018-5711
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5711
Type: osv

## Details
gd_gif_in.c in the GD Graphics Library (aka libgd), as used in PHP before 5.6.33, 7.0.x before 7.0.27, 7.1.x before 7.1.13, and 7.2.x before 7.2.1, has an integer signedness error that leads to an infinite loop via a crafted GIF file, as demonstrated by a call to the imagecreatefromgif or imagecreatefromstring PHP function. This is related to GetCode_ and gdImageCreateFromGifCtx.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3CZ2QADQTKRHTGB2AHD7J4QQNDLBEMM6/
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://access.redhat.com/errata/RHSA-2019:2519
- https://lists.debian.org/debian-lts-announce/2018/01/msg00022.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00028.html
- https://security.gentoo.org/glsa/201903-18
- https://usn.ubuntu.com/3755-1/
- https://bugs.php.net/bug.php?id=75571

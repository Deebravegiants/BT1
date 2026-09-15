# [C] CVE-2018-19409

## Summary
Severity: Critical
Advisory: CVE-2018-19409
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-21
Source: https://osv.dev/vulnerability/CVE-2018-19409
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 9.26. LockSafetyParams is not checked correctly if another device is used.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=661e8d8fb8248c38d67958beda32f3a5876d0c3f
- http://www.securityfocus.com/bid/105990
- https://lists.debian.org/debian-lts-announce/2018/11/msg00036.html
- https://www.ghostscript.com/doc/9.26/History9.htm#Version9.26
- https://access.redhat.com/errata/RHSA-2018:3834
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3831-1/
- https://www.debian.org/security/2018/dsa-4346
- https://bugs.ghostscript.com/show_bug.cgi?id=700176

# [H] CVE-2018-19475

## Summary
Severity: High
Advisory: CVE-2018-19475
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/CVE-2018-19475
Type: osv

## Details
psi/zdevice2.c in Artifex Ghostscript before 9.26 allows remote attackers to bypass intended access restrictions because available stack space is not checked when the device remains the same.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=aeea342904978c9fe17d85f4906a0f6fcce2d315
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=3005fcb9bb160af199e761e03bc70a9f249a987e
- https://access.redhat.com/errata/RHSA-2019:0229
- http://www.securityfocus.com/bid/106154
- https://access.redhat.com/errata/RHBA-2019:0327
- https://lists.debian.org/debian-lts-announce/2018/11/msg00036.html
- https://usn.ubuntu.com/3831-1/
- https://www.debian.org/security/2018/dsa-4346
- https://www.ghostscript.com/doc/9.26/History9.htm#Version9.26
- https://bugs.ghostscript.com/show_bug.cgi?id=700153
- https://semmle.com/news/semmle-discovers-severe-vulnerability-ghostscript-postscript-pdf

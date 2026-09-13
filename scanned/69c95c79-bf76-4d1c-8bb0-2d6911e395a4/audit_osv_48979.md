# [H] CVE-2018-19477

## Summary
Severity: High
Advisory: CVE-2018-19477
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/CVE-2018-19477
Type: osv

## Details
psi/zfjbig2.c in Artifex Ghostscript before 9.26 allows remote attackers to bypass intended access restrictions because of a JBIG2Decode type confusion.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=ef252e7dc214bcbd9a2539216aab9202848602bb
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=606a22e77e7f081781e99e44644cd0119f559e03
- http://www.securityfocus.com/bid/106154
- https://access.redhat.com/errata/RHSA-2019:0229
- https://lists.debian.org/debian-lts-announce/2018/11/msg00036.html
- https://usn.ubuntu.com/3831-1/
- https://www.ghostscript.com/doc/9.26/History9.htm#Version9.26
- https://access.redhat.com/errata/RHBA-2019:0327
- https://www.debian.org/security/2018/dsa-4346
- https://bugs.ghostscript.com/show_bug.cgi?id=700168
- https://semmle.com/news/semmle-discovers-severe-vulnerability-ghostscript-postscript-pdf

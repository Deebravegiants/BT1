# [H] CVE-2018-19476

## Summary
Severity: High
Advisory: CVE-2018-19476
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/CVE-2018-19476
Type: osv

## Details
psi/zicc.c in Artifex Ghostscript before 9.26 allows remote attackers to bypass intended access restrictions because of a setcolorspace type confusion.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=67d760ab775dae4efe803b5944b0439aa3c0b04a
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=434753adbe8be5534bfb9b7d91746023e8073d16
- http://www.securityfocus.com/bid/106154
- https://lists.debian.org/debian-lts-announce/2018/11/msg00036.html
- https://usn.ubuntu.com/3831-1/
- https://www.debian.org/security/2018/dsa-4346
- https://www.ghostscript.com/doc/9.26/History9.htm#Version9.26
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0229
- https://bugs.ghostscript.com/show_bug.cgi?id=700169
- https://semmle.com/news/semmle-discovers-severe-vulnerability-ghostscript-postscript-pdf

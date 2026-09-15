# [H] CVE-2018-16511

## Summary
Severity: High
Advisory: CVE-2018-16511
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16511
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 9.24. A type confusion in "ztype" could be used by remote attackers able to supply crafted PostScript to crash the interpreter or possibly have unspecified other impact.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=0edd3d6c634a577db261615a9dc2719bca7f6e01
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://access.redhat.com/errata/RHSA-2018:3650
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://bugs.ghostscript.com/show_bug.cgi?id=699659
- https://www.artifex.com/news/ghostscript-security-resolved/
- http://seclists.org/oss-sec/2018/q3/182

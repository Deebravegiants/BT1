# [H] CVE-2018-16540

## Summary
Severity: High
Advisory: CVE-2018-16540
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16540
Type: osv

## Details
In Artifex Ghostscript before 9.24, attackers able to supply crafted PostScript files to the builtin PDF14 converter could use a use-after-free in copydevice handling to crash the interpreter or possibly have unspecified other impact.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=c432131c3fdb2143e148e8ba88555f7f7a63b25e
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0229
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=699661
- https://www.artifex.com/news/ghostscript-security-resolved/

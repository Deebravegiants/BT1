# [M] CVE-2018-16541

## Summary
Severity: Medium
Advisory: CVE-2018-16541
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16541
Type: osv

## Details
In Artifex Ghostscript before 9.24, attackers able to supply crafted PostScript files could use incorrect free logic in pagedevice replacement to crash the interpreter.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=241d91112771a6104de10b3948c3f350d6690c1d
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://access.redhat.com/errata/RHSA-2018:3834
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://bugs.ghostscript.com/show_bug.cgi?id=699664
- https://www.artifex.com/news/ghostscript-security-resolved/

# [M] CVE-2018-16539

## Summary
Severity: Medium
Advisory: CVE-2018-16539
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16539
Type: osv

## Details
In Artifex Ghostscript before 9.24, attackers able to supply crafted PostScript files could use incorrect access checking in temp file handling to disclose contents of files on the system otherwise not readable.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=a054156d425b4dbdaaa9fda4b5f1182b27598c2b
- https://access.redhat.com/errata/RHSA-2018:3650
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://security.gentoo.org/glsa/201811-12
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4288
- https://bugs.ghostscript.com/show_bug.cgi?id=699658
- https://www.artifex.com/news/ghostscript-security-resolved/

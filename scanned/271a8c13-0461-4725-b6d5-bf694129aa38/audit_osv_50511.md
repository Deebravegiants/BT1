# [M] CVE-2020-16291

## Summary
Severity: Medium
Advisory: CVE-2020-16291
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-16291
Type: osv

## Details
A buffer overflow vulnerability in contrib/gdevdj9.c of Artifex Software GhostScript v9.18 to v9.50 allows a remote attacker to cause a denial of service via a crafted PDF file. This is fixed in v9.51.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/tree/contrib/gdevdj9.c?h=ghostpdl-9.18#n824
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=4f73e8b4d578e69a17f452fa60d2130c5faaefd6
- http://git.ghostscript.com/?p=ghostpdl.git;h=4f73e8b4d578e69a17f452fa60d2130c5faaefd6
- https://lists.debian.org/debian-lts-announce/2020/08/msg00032.html
- https://security.gentoo.org/glsa/202008-20
- https://usn.ubuntu.com/4469-1/
- https://www.debian.org/security/2020/dsa-4748
- https://bugs.ghostscript.com/show_bug.cgi?id=701787
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=4f73e8b4d578e69a17f452fa60d2130c5faaefd6

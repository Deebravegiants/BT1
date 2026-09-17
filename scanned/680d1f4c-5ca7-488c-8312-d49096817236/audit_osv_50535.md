# [M] CVE-2020-17538

## Summary
Severity: Medium
Advisory: CVE-2020-17538
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-17538
Type: osv

## Details
A buffer overflow vulnerability in GetNumSameData() in contrib/lips4/gdevlips.c of Artifex Software GhostScript from v9.18 to v9.50 allows a remote attacker to cause a denial of service via a crafted PDF file. This is fixed in v9.51.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/tree/contrib/lips4/gdevlips.c?h=ghostscript-9.18#n148
- https://git.ghostscript.com/?p=ghostpdl.git;a=commit;h=9f39ed4a92578a020ae10459643e1fe72573d134
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=9f39ed4a92578a020ae10459643e1fe72573d134
- https://lists.debian.org/debian-lts-announce/2020/08/msg00032.html
- https://security.gentoo.org/glsa/202008-20
- https://usn.ubuntu.com/4469-1/
- https://www.debian.org/security/2020/dsa-4748
- https://bugs.ghostscript.com/show_bug.cgi?id=701792

# [M] CVE-2020-16306

## Summary
Severity: Medium
Advisory: CVE-2020-16306
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-16306
Type: osv

## Details
A null pointer dereference vulnerability in devices/gdevtsep.c of Artifex Software GhostScript v9.50 allows a remote attacker to cause a denial of service via a crafted postscript file. This is fixed in v9.51.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=aadb53eb834b3def3ef68d78865ff87a68901804
- https://lists.debian.org/debian-lts-announce/2020/08/msg00032.html
- https://security.gentoo.org/glsa/202008-20
- https://usn.ubuntu.com/4469-1/
- https://www.debian.org/security/2020/dsa-4748
- https://bugs.ghostscript.com/show_bug.cgi?id=701821

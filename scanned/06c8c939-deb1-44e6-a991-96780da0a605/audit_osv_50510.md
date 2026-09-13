# [M] CVE-2020-16290

## Summary
Severity: Medium
Advisory: CVE-2020-16290
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-16290
Type: osv

## Details
A buffer overflow vulnerability in jetp3852_print_page() in devices/gdev3852.c of Artifex Software GhostScript v9.50 allows a remote attacker to cause a denial of service via a crafted PDF file. This is fixed in v9.51.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Bh=93cb0c0adbd9bcfefd021d59c472388f67d3300d
- https://usn.ubuntu.com/4469-1/
- https://www.debian.org/security/2020/dsa-4748
- https://lists.debian.org/debian-lts-announce/2020/08/msg00032.html
- https://security.gentoo.org/glsa/202008-20
- https://bugs.ghostscript.com/show_bug.cgi?id=701786

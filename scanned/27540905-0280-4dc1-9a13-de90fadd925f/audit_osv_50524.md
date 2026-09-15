# [M] CVE-2020-16304

## Summary
Severity: Medium
Advisory: CVE-2020-16304
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-16304
Type: osv

## Details
A buffer overflow vulnerability in image_render_color_thresh() in base/gxicolor.c of Artifex Software GhostScript v9.18 to v9.50 allows a remote attacker to escalate privileges via a crafted eps file. This is fixed in v9.51.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=027c546e0dd11e0526f1780a7f3c2c66acffe209
- http://git.ghostscript.com/?p=ghostpdl.git;a=commitdiff;h=027c546e0dd11e0526f1780a7f3c2c66acffe209
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/tree/base/gxicolor.c?h=ghostscript-9.18#n825
- https://www.debian.org/security/2020/dsa-4748
- https://lists.debian.org/debian-lts-announce/2020/08/msg00032.html
- https://security.gentoo.org/glsa/202008-20
- https://usn.ubuntu.com/4469-1/
- https://bugs.ghostscript.com/show_bug.cgi?id=701816

# [H] CVE-2019-13290

## Summary
Severity: High
Advisory: CVE-2019-13290
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-04
Source: https://osv.dev/vulnerability/CVE-2019-13290
Type: osv

## Details
Artifex MuPDF 1.15.0 has a heap-based buffer overflow in fz_append_display_node located at fitz/list-device.c, allowing remote attackers to execute arbitrary code via a crafted PDF file. This occurs with a large BDC property name that overflows the allocated size of a display list node.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=aaf794439e40a2ef544f15b50c20e657414dec7a
- http://git.ghostscript.com/?p=mupdf.git%3Bh=ed19bc806809ad10c4ddce515d375581b86ede85
- https://lists.debian.org/debian-lts-announce/2020/07/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUXKCY35PKC32IFHN4RBUCZ75OWEYVJH/
- https://www.debian.org/security/2020/dsa-4753
- https://bugs.ghostscript.com/show_bug.cgi?id=701118
- https://archive.today/oi6bm

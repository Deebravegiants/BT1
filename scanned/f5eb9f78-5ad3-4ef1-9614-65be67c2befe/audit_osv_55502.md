# [M] CVE-2025-59799

## Summary
Severity: Medium
Advisory: CVE-2025-59799
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-59799
Type: osv

## Details
Artifex Ghostscript through 10.05.1 has a stack-based buffer overflow in pdfmark_coerce_dest in devices/vector/gdevpdfm.c via a large size value.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00010.html
- https://bugs.ghostscript.com/show_bug.cgi?id=708517
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=6dab38fb211f15226c242ab7a83fa53e4b0ff781

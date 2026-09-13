# [M] CVE-2025-59800

## Summary
Severity: Medium
Advisory: CVE-2025-59800
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-59800
Type: osv

## Details
In Artifex Ghostscript through 10.05.1, ocr_begin_page in devices/gdevpdfocr.c has an integer overflow that leads to a heap-based buffer overflow in ocr_line8.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=708602
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=176cf0188a2294bc307b8caec876f39412e58350

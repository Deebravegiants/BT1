# [M] ALPINE-CVE-2025-59800

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-59800
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59800
Type: osv

## Affected
- Alpine:v3.23: `ghostscript` — affected >=0 <10.06.0-r0

## Details
In Artifex Ghostscript through 10.05.1, ocr_begin_page in devices/gdevpdfocr.c has an integer overflow that leads to a heap-based buffer overflow in ocr_line8.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59800

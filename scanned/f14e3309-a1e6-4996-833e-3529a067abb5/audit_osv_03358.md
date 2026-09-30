# [M] ALPINE-CVE-2025-59799

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-59799
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59799
Type: osv

## Affected
- Alpine:v3.23: `ghostscript` — affected >=0 <10.06.0-r0

## Details
Artifex Ghostscript through 10.05.1 has a stack-based buffer overflow in pdfmark_coerce_dest in devices/vector/gdevpdfm.c via a large size value.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59799

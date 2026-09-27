# [H] ALPINE-CVE-2017-17858

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17858
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17858
Type: osv

## Affected
- Alpine:v3.10: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.11: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.7: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.8: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.9: `mupdf` — affected >=0 <1.13-r0

## Details
Heap-based buffer overflow in the ensure_solid_xref function in pdf/pdf-xref.c in Artifex MuPDF 1.12.0 allows a remote attacker to potentially execute arbitrary code via a crafted PDF file, because xref subsection object numbers are unrestricted.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17858

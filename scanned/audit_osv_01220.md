# [M] ALPINE-CVE-2018-6544

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-6544
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6544
Type: osv

## Affected
- Alpine:v3.10: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.11: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.7: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.8: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.9: `mupdf` — affected >=0 <1.13-r0

## Details
pdf_load_obj_stm in pdf/pdf-xref.c in Artifex MuPDF 1.12.0 could reference the object stream recursively and therefore run out of error stack, which allows remote attackers to cause a denial of service via a crafted PDF document.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6544

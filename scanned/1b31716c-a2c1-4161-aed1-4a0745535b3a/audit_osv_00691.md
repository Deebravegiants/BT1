# [H] ALPINE-CVE-2017-5991

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5991
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5991
Type: osv

## Affected
- Alpine:v3.10: `mupdf` — affected >=0 <1.10a-r2
- Alpine:v3.11: `mupdf` — affected >=0 <1.10a-r2
- Alpine:v3.5: `mupdf` — affected >=0 <1.10a-r2
- Alpine:v3.6: `mupdf` — affected >=0 <1.10a-r2
- Alpine:v3.7: `mupdf` — affected >=0 <1.10a-r2
- Alpine:v3.8: `mupdf` — affected >=0 <1.10a-r2
- Alpine:v3.9: `mupdf` — affected >=0 <1.10a-r2

## Details
An issue was discovered in Artifex MuPDF before 1912de5f08e90af1d9d0a9791f58ba3afdb9d465. The pdf_run_xobject function in pdf-op-run.c encounters a NULL pointer dereference during a Fitz fz_paint_pixmap_with_mask painting operation. Versions 1.11 and later are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5991

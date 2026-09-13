# [M] ALPINE-CVE-2017-5896

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-5896
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5896
Type: osv

## Affected
- Alpine:v3.10: `mupdf` — affected >=0 <1.10a-r1
- Alpine:v3.11: `mupdf` — affected >=0 <1.10a-r1
- Alpine:v3.5: `mupdf` — affected >=0 <1.10a-r1
- Alpine:v3.6: `mupdf` — affected >=0 <1.10a-r1
- Alpine:v3.7: `mupdf` — affected >=0 <1.10a-r1
- Alpine:v3.8: `mupdf` — affected >=0 <1.10a-r1
- Alpine:v3.9: `mupdf` — affected >=0 <1.10a-r1

## Details
Heap-based buffer overflow in the fz_subsample_pixmap function in fitz/pixmap.c in MuPDF 1.10a allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted image.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5896

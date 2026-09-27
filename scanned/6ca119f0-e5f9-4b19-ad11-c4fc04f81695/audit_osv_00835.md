# [H] ALPINE-CVE-2017-9935

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9935
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9935
Type: osv

## Affected
- Alpine:v3.10: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.11: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.12: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.13: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.14: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.15: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.16: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.17: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.18: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.19: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.20: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.21: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.22: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.23: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.24: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.5: `tiff` — affected >=0 <4.0.9-r5
- Alpine:v3.6: `tiff` — affected >=0 <4.0.9-r5
- Alpine:v3.7: `tiff` — affected >=0 <4.0.9-r5
- Alpine:v3.8: `tiff` — affected >=0 <4.0.9-r6
- Alpine:v3.9: `tiff` — affected >=0 <4.0.9-r6

## Details
In LibTIFF 4.0.8, there is a heap-based buffer overflow in the t2p_write_pdf function in tools/tiff2pdf.c. This heap overflow could lead to different damages. For example, a crafted TIFF document can lead to an out-of-bounds read in TIFFCleanup, an invalid free in TIFFClose or t2p_free, memory corruption in t2p_readwrite_pdf_image, or a double free in t2p_free. Given these possibilities, it probably could cause arbitrary code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9935

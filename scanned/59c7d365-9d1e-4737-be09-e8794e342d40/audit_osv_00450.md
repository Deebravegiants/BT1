# [M] ALPINE-CVE-2017-12982

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-12982
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12982
Type: osv

## Affected
- Alpine:v3.10: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.11: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.12: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.13: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.14: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.15: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.16: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.17: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.18: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.19: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.20: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.21: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.22: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.23: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.24: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.3: `openjpeg` — affected >=0 <2.1.2-r2
- Alpine:v3.4: `openjpeg` — affected >=0 <2.1.2-r2
- Alpine:v3.5: `openjpeg` — affected >=0 <2.1.2-r2
- Alpine:v3.6: `openjpeg` — affected >=0 <2.1.2-r2
- Alpine:v3.7: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.8: `openjpeg` — affected >=0 <2.2.0-r1
- Alpine:v3.9: `openjpeg` — affected >=0 <2.2.0-r1

## Details
The bmp_read_info_header function in bin/jp2/convertbmp.c in OpenJPEG 2.2.0 does not reject headers with a zero biBitCount, which allows remote attackers to cause a denial of service (memory allocation failure) in the opj_image_create function in lib/openjp2/image.c, related to the opj_aligned_alloc_n function in opj_malloc.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12982

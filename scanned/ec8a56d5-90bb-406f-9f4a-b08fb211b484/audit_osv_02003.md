# [H] ALPINE-CVE-2020-6851

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-6851
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-6851
Type: osv

## Affected
- Alpine:v3.10: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.11: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.12: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.13: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.14: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.15: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.16: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.17: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.18: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.19: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.20: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.21: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.22: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.23: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.24: `openjpeg` — affected >=0 <2.3.1-r3
- Alpine:v3.8: `openjpeg` — affected >=0 <2.3.0-r4
- Alpine:v3.9: `openjpeg` — affected >=0 <2.3.0-r5

## Details
OpenJPEG through 2.3.1 has a heap-based buffer overflow in opj_t1_clbl_decode_processor in openjp2/t1.c because of lack of opj_j2k_update_image_dimensions validation.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-6851

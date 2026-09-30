# [H] ALPINE-CVE-2017-14151

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14151
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14151
Type: osv

## Affected
- Alpine:v3.10: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.11: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.12: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.13: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.14: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.15: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.16: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.17: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.18: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.19: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.20: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.21: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.22: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.23: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.24: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.3: `openjpeg` — affected >=0 <2.2.0-r0
- Alpine:v3.4: `openjpeg` — affected >=0 <2.2.0-r0
- Alpine:v3.5: `openjpeg` — affected >=0 <2.2.0-r0
- Alpine:v3.6: `openjpeg` — affected >=0 <2.2.0-r0
- Alpine:v3.7: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.8: `openjpeg` — affected >=0 <2.2.0-r2
- Alpine:v3.9: `openjpeg` — affected >=0 <2.2.0-r2

## Details
An off-by-one error was discovered in opj_tcd_code_block_enc_allocate_data in lib/openjp2/tcd.c in OpenJPEG 2.2.0. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service (heap-based buffer overflow affecting opj_mqc_flush in lib/openjp2/mqc.c and opj_t1_encode_cblk in lib/openjp2/t1.c) or possibly remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14151

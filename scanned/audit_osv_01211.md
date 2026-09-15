# [M] ALPINE-CVE-2018-5785

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5785
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5785
Type: osv

## Affected
- Alpine:v3.10: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.11: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.12: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.13: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.14: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.15: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.16: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.17: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.18: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.19: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.20: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.21: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.22: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.23: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.24: `openjpeg` — affected >=0 <2.3.0-r3
- Alpine:v3.6: `openjpeg` — affected >=0 <2.3.0-r2
- Alpine:v3.7: `openjpeg` — affected >=0 <2.3.0-r2
- Alpine:v3.8: `openjpeg` — affected >=0 <2.3.0-r2
- Alpine:v3.9: `openjpeg` — affected >=0 <2.3.0-r3

## Details
In OpenJPEG 2.3.0, there is an integer overflow caused by an out-of-bounds left shift in the opj_j2k_setup_encoder function (openjp2/j2k.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5785

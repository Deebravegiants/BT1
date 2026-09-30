# [H] ALPINE-CVE-2023-49468

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-49468
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49468
Type: osv

## Affected
- Alpine:v3.16: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.17: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.18: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.19: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.20: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.21: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.22: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.23: `libde265` — affected >=0 <1.0.15-r0
- Alpine:v3.24: `libde265` — affected >=0 <1.0.15-r0

## Details
Libde265 v1.0.14 was discovered to contain a global buffer overflow vulnerability in the read_coding_unit function at slice.cc.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49468

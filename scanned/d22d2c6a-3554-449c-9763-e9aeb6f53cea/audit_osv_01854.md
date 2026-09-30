# [M] ALPINE-CVE-2020-21596

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-21596
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-21596
Type: osv

## Affected
- Alpine:v3.14: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.15: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.16: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.17: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.18: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.19: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.20: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.21: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.22: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.23: `libde265` — affected >=0 <1.0.11-r0
- Alpine:v3.24: `libde265` — affected >=0 <1.0.11-r0

## Details
libde265 v1.0.4 contains a global buffer overflow in the decode_CABAC_bit function, which can be exploited via a crafted a file.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-21596

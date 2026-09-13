# [H] ALPINE-CVE-2023-27103

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-27103
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27103
Type: osv

## Affected
- Alpine:v3.14: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.15: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.16: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.17: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.18: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.19: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.20: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.21: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.22: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.23: `libde265` — affected >=0 <1.0.11-r1
- Alpine:v3.24: `libde265` — affected >=0 <1.0.11-r1

## Details
Libde265 v1.0.11 was discovered to contain a heap buffer overflow via the function derive_collocated_motion_vectors at motion.cc.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27103

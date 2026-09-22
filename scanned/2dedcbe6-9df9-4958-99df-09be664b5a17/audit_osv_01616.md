# [M] ALPINE-CVE-2019-6462

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6462
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6462
Type: osv

## Affected
- Alpine:v3.12: `cairo` — affected >=0 <1.16.0-r5
- Alpine:v3.13: `cairo` — affected >=0 <1.16.0-r4
- Alpine:v3.14: `cairo` — affected >=0 <1.16.0-r5
- Alpine:v3.15: `cairo` — affected >=0 <1.16.0-r5
- Alpine:v3.16: `cairo` — affected >=0 <1.17.4-r2
- Alpine:v3.17: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.18: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.19: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.20: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.21: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.22: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.23: `cairo` — affected >=0 <1.17.4-r1
- Alpine:v3.24: `cairo` — affected >=0 <1.17.4-r1

## Details
An issue was discovered in cairo 1.16.0. There is an infinite loop in the function _arc_error_normalized in the file cairo-arc.c, related to _arc_max_angle_for_tolerance_normalized.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6462

# [C] ALPINE-CVE-2020-9366

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-9366
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-9366
Type: osv

## Affected
- Alpine:v3.10: `screen` — affected >=0 <4.6.2-r1
- Alpine:v3.11: `screen` — affected >=0 <4.7.0-r1
- Alpine:v3.12: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.13: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.14: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.15: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.16: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.17: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.18: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.19: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.20: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.21: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.22: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.23: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.24: `screen` — affected >=0 <4.8.0-r0
- Alpine:v3.8: `screen` — affected >=0 <4.6.2-r1
- Alpine:v3.9: `screen` — affected >=0 <4.6.2-r1

## Details
A buffer overflow was found in the way GNU Screen before 4.8.0 treated the special escape OSC 49. Specially crafted output, or a special program, could corrupt memory and crash Screen or possibly have unspecified other impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-9366

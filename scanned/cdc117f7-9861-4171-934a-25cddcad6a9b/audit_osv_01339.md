# [C] ALPINE-CVE-2019-11234

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-11234
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11234
Type: osv

## Affected
- Alpine:v3.10: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.11: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.12: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.13: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.14: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.15: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.16: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.17: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.18: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.19: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.20: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.21: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.22: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.23: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.24: `freeradius` — affected >=0 <3.0.19-r0
- Alpine:v3.6: `freeradius` — affected >=0 <3.0.13-r3
- Alpine:v3.7: `freeradius` — affected >=0 <3.0.15-r4
- Alpine:v3.8: `freeradius` — affected >=0 <3.0.17-r3
- Alpine:v3.9: `freeradius` — affected >=0 <3.0.17-r5

## Details
FreeRADIUS before 3.0.19 does not prevent use of reflection for authentication spoofing, aka a "Dragonblood" issue, a similar issue to CVE-2019-9497.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11234

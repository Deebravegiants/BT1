# [M] ALPINE-CVE-2019-6471

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6471
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6471
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.11.0 <9.14.3-r0
- Alpine:v3.11: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.12: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.13: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.14: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.15: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.16: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.17: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.18: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.19: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.20: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.21: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.22: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.23: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.24: `bind` — affected >=9.11.0 <9.14.4-r0
- Alpine:v3.7: `bind` — affected >=9.11.0 <9.11.8-r0
- Alpine:v3.8: `bind` — affected >=9.11.0 <9.12.4_p2-r0
- Alpine:v3.9: `bind` — affected >=9.11.0 <9.12.4_p2-r0

## Details
A race condition which may occur when discarding malformed packets can result in BIND exiting due to a REQUIRE assertion failure in dispatch.c. Versions affected: BIND 9.11.0 -> 9.11.7, 9.12.0 -> 9.12.4-P1, 9.14.0 -> 9.14.2. Also all releases of the BIND 9.13 development branch and version 9.15.0 of the BIND 9.15 development branch and BIND Supported Preview Edition versions 9.11.3-S1 -> 9.11.7-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6471

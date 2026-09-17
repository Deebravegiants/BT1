# [M] ALPINE-CVE-2019-6465

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6465
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6465
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.11: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.12: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.13: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.14: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.15: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.16: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.17: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.18: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.19: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.20: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.21: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.22: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.23: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.24: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.6: `bind` — affected >=9.9.0 <9.11.5_p4-r0
- Alpine:v3.7: `bind` — affected >=9.9.0 <9.11.5_p4-r0
- Alpine:v3.8: `bind` — affected >=9.9.0 <9.12.3_p4-r0
- Alpine:v3.9: `bind` — affected >=9.9.0 <9.12.3_p4-r0

## Details
Controls for zone transfers may not be properly applied to Dynamically Loadable Zones (DLZs) if the zones are writable Versions affected: BIND 9.9.0 -> 9.10.8-P1, 9.11.0 -> 9.11.5-P2, 9.12.0 -> 9.12.3-P2, and versions 9.9.3-S1 -> 9.11.5-S3 of BIND 9 Supported Preview Edition. Versions 9.13.0 -> 9.13.6 of the 9.13 development branch are also affected. Versions prior to BIND 9.9.0 have not been evaluated for vulnerability to CVE-2019-6465.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6465

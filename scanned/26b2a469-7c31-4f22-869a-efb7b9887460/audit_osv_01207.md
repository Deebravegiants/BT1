# [H] ALPINE-CVE-2018-5744

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5744
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5744
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.11: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.12: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.13: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.14: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.15: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.16: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.17: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.18: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.19: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.20: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.21: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.22: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.23: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.24: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.6: `bind` — affected >=9.10.7 <9.11.5_p4-r0
- Alpine:v3.7: `bind` — affected >=9.10.7 <9.11.5_p4-r0
- Alpine:v3.8: `bind` — affected >=9.10.7 <9.12.3_p4-r0
- Alpine:v3.9: `bind` — affected >=9.10.7 <9.12.3_p4-r0

## Details
A failure to free memory can occur when processing messages having a specific combination of EDNS options. Versions affected are: BIND 9.10.7 -> 9.10.8-P1, 9.11.3 -> 9.11.5-P1, 9.12.0 -> 9.12.3-P1, and versions 9.10.7-S1 -> 9.11.5-S3 of BIND 9 Supported Preview Edition. Versions 9.13.0 -> 9.13.6 of the 9.13 development branch are also affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5744

# [H] ALPINE-CVE-2018-5743

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5743
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5743
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.11: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.12: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.13: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.14: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.15: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.16: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.17: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.18: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.19: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.20: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.21: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.22: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.23: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.24: `bind` — affected >=9.9.0 <9.14.1-r0
- Alpine:v3.6: `bind` — affected >=9.9.0 <9.11.6_p1-r0
- Alpine:v3.7: `bind` — affected >=9.9.0 <9.11.6_p1-r0
- Alpine:v3.8: `bind` — affected >=9.9.0 <9.12.4_p1-r0
- Alpine:v3.9: `bind` — affected >=9.9.0 <9.12.4_p1-r0

## Details
By design, BIND is intended to limit the number of TCP clients that can be connected at any given time. The number of allowed connections is a tunable parameter which, if unset, defaults to a conservative value for most servers. Unfortunately, the code which was intended to limit the number of simultaneous connections contained an error which could be exploited to grow the number of simultaneous connections beyond this limit. Versions affected: BIND 9.9.0 -> 9.10.8-P1, 9.11.0 -> 9.11.6, 9.12.0 -> 9.12.4, 9.14.0. BIND 9 Supported Preview Edition versions 9.9.3-S1 -> 9.11.5-S3, and 9.11.5-S5. Versions 9.13.0 -> 9.13.7 of the 9.13 development branch are also affected. Versions prior to BIND 9.9.0 have not been evaluated for vulnerability to CVE-2018-5743.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5743

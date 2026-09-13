# [M] ALPINE-CVE-2021-28116

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28116
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28116
Type: osv

## Affected
- Alpine:v3.11: `squid` — affected >=5.0 <4.17-r0
- Alpine:v3.12: `squid` — affected >=5.0 <4.17-r0
- Alpine:v3.13: `squid` — affected >=5.0 <5.0.6-r1
- Alpine:v3.14: `squid` — affected >=5.0 <5.0.6-r1
- Alpine:v3.15: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.16: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.17: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.18: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.19: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.20: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.21: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.22: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.23: `squid` — affected >=5.0 <5.2-r0
- Alpine:v3.24: `squid` — affected >=5.0 <5.2-r0

## Details
Squid through 4.14 and 5.x through 5.0.5, in some configurations, allows information disclosure because of an out-of-bounds read in WCCP protocol data. This can be leveraged as part of a chain for remote code execution as nobody.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28116

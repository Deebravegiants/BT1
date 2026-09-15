# [M] ALPINE-CVE-2018-5388

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5388
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5388
Type: osv

## Affected
- Alpine:v3.10: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.11: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.12: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.13: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.14: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.15: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.16: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.17: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.18: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.19: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.20: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.21: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.22: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.23: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.24: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.7: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.8: `strongswan` — affected >=0 <5.6.3-r0
- Alpine:v3.9: `strongswan` — affected >=0 <5.6.3-r0

## Details
In stroke_socket.c in strongSwan before 5.6.3, a missing packet length check could allow a buffer underflow, which may lead to resource exhaustion and denial of service while reading from the socket.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5388

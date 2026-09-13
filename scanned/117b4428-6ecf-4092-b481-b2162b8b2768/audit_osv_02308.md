# [H] ALPINE-CVE-2021-41990

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41990
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41990
Type: osv

## Affected
- Alpine:v3.12: `strongswan` — affected >=5.6.1 <5.8.4-r3
- Alpine:v3.13: `strongswan` — affected >=5.6.1 <5.9.1-r1
- Alpine:v3.14: `strongswan` — affected >=5.6.1 <5.9.1-r2
- Alpine:v3.15: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.16: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.17: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.18: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.19: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.20: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.21: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.22: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.23: `strongswan` — affected >=5.6.1 <5.9.1-r3
- Alpine:v3.24: `strongswan` — affected >=5.6.1 <5.9.1-r3

## Details
The gmp plugin in strongSwan before 5.9.4 has a remote integer overflow via a crafted certificate with an RSASSA-PSS signature. For example, this can be triggered by an unrelated self-signed CA certificate sent by an initiator. Remote code execution cannot occur.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41990

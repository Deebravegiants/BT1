# [C] ALPINE-CVE-2023-41913

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-41913
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-41913
Type: osv

## Affected
- Alpine:v3.17: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.18: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.19: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.20: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.21: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.22: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.23: `strongswan` — affected >=5.3.0 <5.9.12-r0
- Alpine:v3.24: `strongswan` — affected >=5.3.0 <5.9.12-r0

## Details
strongSwan before 5.9.12 has a buffer overflow and possible unauthenticated remote code execution via a DH public value that exceeds the internal buffer in charon-tkm's DH proxy. The earliest affected version is 5.3.0. An attack can occur via a crafted IKE_SA_INIT message.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-41913

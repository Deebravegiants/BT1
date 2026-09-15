# [C] ALPINE-CVE-2021-45079

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-45079
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-01-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-45079
Type: osv

## Affected
- Alpine:v3.13: `strongswan` — affected >=4.1.2 <5.9.1-r2
- Alpine:v3.14: `strongswan` — affected >=4.1.2 <5.9.1-r3
- Alpine:v3.15: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.16: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.17: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.18: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.19: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.20: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.21: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.22: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.23: `strongswan` — affected >=4.1.2 <5.9.1-r4
- Alpine:v3.24: `strongswan` — affected >=4.1.2 <5.9.1-r4

## Details
In strongSwan before 5.9.5, a malicious responder can send an EAP-Success message too early without actually authenticating the client and (in the case of EAP methods with mutual authentication and EAP-only authentication for IKEv2) even without server authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-45079

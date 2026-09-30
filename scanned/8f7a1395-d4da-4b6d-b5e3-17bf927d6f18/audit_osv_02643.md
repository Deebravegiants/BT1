# [H] ALPINE-CVE-2022-40617

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-40617
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-40617
Type: osv

## Affected
- Alpine:v3.13: `strongswan` — affected >=0 <5.9.1-r2
- Alpine:v3.14: `strongswan` — affected >=0 <5.9.1-r3
- Alpine:v3.15: `strongswan` — affected >=0 <5.9.1-r4
- Alpine:v3.16: `strongswan` — affected >=0 <5.9.5-r2
- Alpine:v3.17: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.18: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.19: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.20: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.21: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.22: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.23: `strongswan` — affected >=0 <5.9.8-r0
- Alpine:v3.24: `strongswan` — affected >=0 <5.9.8-r0

## Details
strongSwan before 5.9.8 allows remote attackers to cause a denial of service in the revocation plugin by sending a crafted end-entity (and intermediate CA) certificate that contains a CRL/OCSP URL that points to a server (under the attacker's control) that doesn't properly respond but (for example) just does nothing after the initial TCP handshake, or sends an excessive amount of application data.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-40617

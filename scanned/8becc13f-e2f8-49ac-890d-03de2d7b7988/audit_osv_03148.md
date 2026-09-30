# [C] ALPINE-CVE-2024-5594

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-5594
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-5594
Type: osv

## Affected
- Alpine:v3.17: `openvpn` — affected >=2.6.0 <2.5.10-r1
- Alpine:v3.18: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.19: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.20: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.6.11-r0

## Details
OpenVPN before 2.6.11 does not santize PUSH_REPLY messages properly which an attacker controlling the server can use to inject unexpected arbitrary data ending up in client logs.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-5594

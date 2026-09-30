# [H] ALPINE-CVE-2025-13086

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-13086
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-13086
Type: osv

## Affected
- Alpine:v3.19: `openvpn` — affected >=2.6.0 <2.6.16-r0
- Alpine:v3.20: `openvpn` — affected >=2.6.0 <2.6.16-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.0 <2.6.16-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.0 <2.6.16-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.0 <2.6.16-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.6.16-r0

## Details
Improper validation of source IP addresses in OpenVPN version 2.6.0 through 2.6.15 and 2.7_alpha1 through 2.7_rc1 allows an attacker to open a session from a different IP address which did not initiate the connection resulting in a denial of service for the originating client

## References
- https://security.alpinelinux.org/vuln/CVE-2025-13086

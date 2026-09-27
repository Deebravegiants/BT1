# [M] ALPINE-CVE-2024-28882

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-28882
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-28882
Type: osv

## Affected
- Alpine:v3.18: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.19: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.20: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.0 <2.6.11-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.6.11-r0

## Details
OpenVPN from 2.6.0 through 2.6.10 in a server role accepts multiple exit notifications from authenticated clients which will extend the validity of a closing session

## References
- https://security.alpinelinux.org/vuln/CVE-2024-28882

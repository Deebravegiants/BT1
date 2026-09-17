# [C] ALPINE-CVE-2023-46850

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-46850
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46850
Type: osv

## Affected
- Alpine:v3.18: `openvpn` — affected >=2.6.0 <2.6.7-r0
- Alpine:v3.19: `openvpn` — affected >=2.6.0 <2.6.7-r0
- Alpine:v3.20: `openvpn` — affected >=2.6.0 <2.6.7-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.0 <2.6.7-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.0 <2.6.7-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.0 <2.6.7-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.6.7-r0

## Details
Use after free in OpenVPN version 2.6.0 to 2.6.6 may lead to undefined behavoir, leaking memory buffers or remote execution when sending network buffers to a remote peer.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46850

# [C] ALPINE-CVE-2022-0547

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-0547
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0547
Type: osv

## Affected
- Alpine:v3.12: `openvpn` — affected >=2.1.0 <2.4.12-r0
- Alpine:v3.13: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.14: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.15: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.16: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.17: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.18: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.19: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.20: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.21: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.22: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.23: `openvpn` — affected >=2.1.0 <2.5.6-r0
- Alpine:v3.24: `openvpn` — affected >=2.1.0 <2.5.6-r0

## Details
OpenVPN 2.1 until v2.4.12 and v2.5.6 may enable authentication bypass in external authentication plug-ins when more than one of them makes use of deferred authentication replies, which allows an external user to be granted access with only partially correct credentials.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0547

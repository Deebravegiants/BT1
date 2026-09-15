# [H] ALPINE-CVE-2018-9336

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-9336
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-9336
Type: osv

## Affected
- Alpine:v3.10: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.11: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.12: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.13: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.14: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.15: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.16: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.17: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.18: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.19: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.20: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.21: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.22: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.23: `openvpn` — affected >=2.4.0 <2.4.6-r0
- Alpine:v3.24: `openvpn` — affected >=2.4.0 <2.4.6-r0

## Details
openvpnserv.exe (aka the interactive service helper) in OpenVPN 2.4.x before 2.4.6 allows a local attacker to cause a double-free of memory by sending a malformed request to the interactive service. This could cause a denial-of-service through memory corruption or possibly have unspecified other impact including privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-9336

# [H] ALPINE-CVE-2023-46849

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-46849
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46849
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
Using the --fragment option in certain configuration setups OpenVPN version 2.6.0 to 2.6.6 allows an attacker to trigger a divide by zero behaviour which could cause an application crash, leading to a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46849

# [H] ALPINE-CVE-2025-2704

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-2704
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-2704
Type: osv

## Affected
- Alpine:v3.19: `openvpn` — affected >=2.6.1 <2.6.16-r0
- Alpine:v3.20: `openvpn` — affected >=2.6.1 <2.6.16-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.1 <2.6.14-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.1 <2.6.14-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.1 <2.6.14-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.1 <2.6.14-r0

## Details
OpenVPN version 2.6.1 through 2.6.13 in server mode using TLS-crypt-v2 allows remote attackers to trigger a denial of service by corrupting and replaying network packets in the early handshake phase

## References
- https://security.alpinelinux.org/vuln/CVE-2025-2704

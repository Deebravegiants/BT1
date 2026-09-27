# [M] ALPINE-CVE-2026-35058

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-35058
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-35058
Type: osv

## Affected
- Alpine:v3.20: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.6.20-r0

## Details
Improper validation of packet length during tls-crypt-v2 key extraction in OpenVPN 2.6.0 through 2.6.19 and 2.7_alpha1 through 2.7.1 allows authenticated attackers to trigger a fatal assertion and cause a denial of service via a specially crafted packet.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-35058

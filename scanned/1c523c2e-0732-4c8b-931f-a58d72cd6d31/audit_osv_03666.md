# [H] ALPINE-CVE-2026-40215

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-40215
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40215
Type: osv

## Affected
- Alpine:v3.20: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.21: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.22: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.23: `openvpn` — affected >=2.6.0 <2.6.20-r0
- Alpine:v3.24: `openvpn` — affected >=2.6.0 <2.6.20-r0

## Details
A race condition in OpenVPN 2.6.0 through 2.6.19 and 2.7_alpha1 through 2.7.1 allows remote attackers to potentially cause a server crash or leak heap memory via a use-after-free triggered during TLS session promotion.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40215

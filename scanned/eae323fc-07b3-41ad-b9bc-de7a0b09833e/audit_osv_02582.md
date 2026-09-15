# [H] ALPINE-CVE-2022-32744

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-32744
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32744
Type: osv

## Affected
- Alpine:v3.15: `samba` — affected >=4.3.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.3.0 <4.15.12-r0
- Alpine:v3.17: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.18: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.19: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.20: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.21: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.22: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.23: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.24: `samba` — affected >=4.3.0 <4.15.9-r0

## Details
A flaw was found in Samba. The KDC accepts kpasswd requests encrypted with any key known to it. By encrypting forged kpasswd requests with its own key, a user can change other users' passwords, enabling full domain takeover.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32744

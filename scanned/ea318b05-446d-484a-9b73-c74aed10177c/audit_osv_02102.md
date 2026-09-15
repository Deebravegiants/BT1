# [H] ALPINE-CVE-2021-23192

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-23192
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23192
Type: osv

## Affected
- Alpine:v3.13: `samba` — affected >=4.10.0 <4.13.17-r0
- Alpine:v3.14: `samba` — affected >=4.10.0 <4.14.12-r0
- Alpine:v3.15: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.16: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.17: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.18: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.19: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.20: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.21: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.22: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.23: `samba` — affected >=4.10.0 <4.15.2-r0
- Alpine:v3.24: `samba` — affected >=4.10.0 <4.15.2-r0

## Details
A flaw was found in the way samba implemented DCE/RPC. If a client to a Samba server sent a very large DCE/RPC request, and chose to fragment it, an attacker could replace later fragments with their own data, bypassing the signature requirements.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23192

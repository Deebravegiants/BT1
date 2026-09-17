# [H] ALPINE-CVE-2021-3738

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3738
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3738
Type: osv

## Affected
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.13.17-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.14.12-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.15.2-r0

## Details
In DCE/RPC it is possible to share the handles (cookies for resource state) between multiple connections via a mechanism called 'association groups'. These handles can reference connections to our sam.ldb database. However while the database was correctly shared, the user credentials state was only pointed at, and when one connection within that association group ended, the database would be left pointing at an invalid 'struct session_info'. The most likely outcome here is a crash, but it is possible that the use-after-free could instead allow different user state to be pointed at and this might allow more privileged access.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3738

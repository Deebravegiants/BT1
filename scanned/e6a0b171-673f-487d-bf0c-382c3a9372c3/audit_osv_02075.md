# [H] ALPINE-CVE-2021-20277

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-20277
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20277
Type: osv

## Affected
- Alpine:v3.12: `samba` — affected >=4.0.0 <4.12.14-r0
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.13.7-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.14.2-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.14.2-r0

## Details
A flaw was found in Samba's libldb. Multiple, consecutive leading spaces in an LDAP attribute can lead to an out-of-bounds memory write, leading to a crash of the LDAP server process handling the request. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20277

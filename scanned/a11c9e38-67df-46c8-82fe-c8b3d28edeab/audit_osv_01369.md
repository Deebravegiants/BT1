# [M] ALPINE-CVE-2019-12436

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12436
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12436
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.11: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.12: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.13: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.14: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.15: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.16: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.17: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.18: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.19: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.20: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.21: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.22: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.23: `samba` — affected >=4.10.0 <4.10.5-r0
- Alpine:v3.24: `samba` — affected >=4.10.0 <4.10.5-r0

## Details
Samba 4.10.x before 4.10.5 has a NULL pointer dereference, leading to an AD DC LDAP server Denial of Service. This is related to an attacker using the paged search control. The attacker must have directory read access in order to attempt an exploit.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12436

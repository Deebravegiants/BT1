# [M] ALPINE-CVE-2018-14628

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14628
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14628
Type: osv

## Affected
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.18.9-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.18.9-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.18.9-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.18.9-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.18.9-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.18.9-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.18.9-r0

## Details
An information leak vulnerability was discovered in Samba's LDAP server. Due to missing access control checks, an authenticated but unprivileged attacker could discover the names and preserved attributes of deleted objects in the LDAP store.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14628

# [M] ALPINE-CVE-2018-14629

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14629
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14629
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.11: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.12: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.6: `samba` — affected >=4.0.0 <4.6.16-r2
- Alpine:v3.7: `samba` — affected >=4.0.0 <4.7.6-r2
- Alpine:v3.8: `samba` — affected >=4.0.0 <4.8.11-r0
- Alpine:v3.9: `samba` — affected >=4.0.0 <4.8.11-r0

## Details
A denial of service vulnerability was discovered in Samba's LDAP server before versions 4.7.12, 4.8.7, and 4.9.3. A CNAME loop could lead to infinite recursion in the server. An unprivileged local attacker could create such an entry, leading to denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14629

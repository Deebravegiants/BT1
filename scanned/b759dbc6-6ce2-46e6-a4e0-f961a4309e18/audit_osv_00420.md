# [H] ALPINE-CVE-2017-12163

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12163
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.1 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12163
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.11: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.12: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.13: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.14: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.15: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.16: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.17: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.18: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.19: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.20: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.21: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.22: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.23: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.24: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.4: `samba` — affected >=4.5.0 <4.4.16-r0
- Alpine:v3.5: `samba` — affected >=4.5.0 <4.5.14-r0
- Alpine:v3.6: `samba` — affected >=4.5.0 <4.6.8-r0
- Alpine:v3.7: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.8: `samba` — affected >=4.5.0 <4.7.0-r0
- Alpine:v3.9: `samba` — affected >=4.5.0 <4.7.0-r0

## Details
An information leak flaw was found in the way SMB1 protocol was implemented by Samba before 4.4.16, 4.5.x before 4.5.14, and 4.6.x before 4.6.8. A malicious client could use this flaw to dump server memory contents to a file on the samba share or to a shared printer, though the exact area of server memory cannot be controlled by the attacker.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12163

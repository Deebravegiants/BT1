# [C] ALPINE-CVE-2019-10197

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-10197
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10197
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.11: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.12: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.13: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.14: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.15: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.16: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.17: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.18: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.19: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.20: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.21: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.22: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.23: `samba` — affected >=4.9.0 <4.10.8-r0
- Alpine:v3.24: `samba` — affected >=4.9.0 <4.10.8-r0

## Details
A flaw was found in samba versions 4.9.x up to 4.9.13, samba 4.10.x up to 4.10.8 and samba 4.11.x up to 4.11.0rc3, when certain parameters were set in the samba configuration file. An unauthenticated attacker could use this flaw to escape the shared directory and access the contents of directories outside the share.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10197

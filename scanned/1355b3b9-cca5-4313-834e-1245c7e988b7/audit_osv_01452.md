# [M] ALPINE-CVE-2019-14902

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14902
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14902
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.0.0 <4.10.12-r0
- Alpine:v3.11: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.12: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.11.5-r0
- Alpine:v3.8: `samba` — affected >=4.0.0 <4.8.12-r2
- Alpine:v3.9: `samba` — affected >=4.0.0 <4.8.12-r2

## Details
There is an issue in all samba 4.11.x versions before 4.11.5, all samba 4.10.x versions before 4.10.12 and all samba 4.9.x versions before 4.9.18, where the removal of the right to create or modify a subtree would not automatically be taken away on all domain controllers.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14902

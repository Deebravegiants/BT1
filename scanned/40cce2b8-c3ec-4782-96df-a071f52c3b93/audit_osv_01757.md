# [M] ALPINE-CVE-2020-14323

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14323
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14323
Type: osv

## Affected
- Alpine:v3.11: `samba` — affected >=3.6.0 <4.11.16-r0
- Alpine:v3.12: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.13: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.14: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.15: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.16: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.17: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.18: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.19: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.20: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.21: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.22: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.23: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.24: `samba` — affected >=3.6.0 <4.12.9-r0

## Details
A null pointer dereference flaw was found in samba's Winbind service in versions before 4.11.15, before 4.12.9 and before 4.13.1. A local user could use this flaw to crash the winbind service causing denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14323

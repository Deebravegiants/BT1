# [M] ALPINE-CVE-2019-19344

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-19344
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19344
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.9.0 <4.10.12-r0
- Alpine:v3.11: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.12: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.13: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.14: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.15: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.16: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.17: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.18: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.19: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.20: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.21: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.22: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.23: `samba` — affected >=4.9.0 <4.11.5-r0
- Alpine:v3.24: `samba` — affected >=4.9.0 <4.11.5-r0

## Details
There is a use-after-free issue in all samba 4.9.x versions before 4.9.18, all samba 4.10.x versions before 4.10.12 and all samba 4.11.x versions before 4.11.5, essentially due to a call to realloc() while other local variables still point at the original buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19344

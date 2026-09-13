# [M] ALPINE-CVE-2021-3671

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3671
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3671
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.14: `samba` — affected >=4.14.0 <4.14.8-r0
- Alpine:v3.15: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.16: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.17: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.18: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.19: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.20: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.21: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.22: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.23: `samba` — affected >=4.14.0 <4.15.0-r0
- Alpine:v3.24: `samba` — affected >=4.14.0 <4.15.0-r0

## Details
A null pointer de-reference was found in the way samba kerberos server handled missing sname in TGS-REQ (Ticket Granting Server - Request). An authenticated user could use this flaw to crash the samba server.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3671

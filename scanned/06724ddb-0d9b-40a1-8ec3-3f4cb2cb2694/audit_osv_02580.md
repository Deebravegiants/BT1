# [M] ALPINE-CVE-2022-32742

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-32742
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32742
Type: osv

## Affected
- Alpine:v3.14: `samba` — affected >=4.15.0 <4.14.14-r0
- Alpine:v3.15: `samba` — affected >=4.15.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.15.0 <4.15.12-r0
- Alpine:v3.17: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.18: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.19: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.20: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.21: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.22: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.23: `samba` — affected >=4.15.0 <4.15.9-r0
- Alpine:v3.24: `samba` — affected >=4.15.0 <4.15.9-r0

## Details
A flaw was found in Samba. Some SMB1 write requests were not correctly range-checked to ensure the client had sent enough data to fulfill the write, allowing server memory contents to be written into the file (or printer) instead of client-supplied data. The client cannot control the area of the server memory written to the file (or printer).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32742

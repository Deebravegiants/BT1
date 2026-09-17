# [M] ALPINE-CVE-2019-10218

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10218
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10218
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.10.0 <4.10.10-r0
- Alpine:v3.11: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.12: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.13: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.14: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.15: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.16: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.17: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.18: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.19: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.20: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.21: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.22: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.23: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.24: `samba` — affected >=4.10.0 <4.11.2-r0
- Alpine:v3.8: `samba` — affected >=4.10.0 <4.8.12-r1
- Alpine:v3.9: `samba` — affected >=4.10.0 <4.8.12-r1

## Details
A flaw was found in the samba client, all samba versions before samba 4.11.2, 4.10.10 and 4.9.15, where a malicious server can supply a pathname to the client with separators. This could allow the client to access files and folders outside of the SMB network pathnames. An attacker could use this vulnerability to create files outside of the current working directory using the privileges of the client user.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10218

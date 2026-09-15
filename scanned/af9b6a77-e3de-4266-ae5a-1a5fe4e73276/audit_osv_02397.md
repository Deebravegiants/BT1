# [H] ALPINE-CVE-2022-2031

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-2031
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-2031
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
A flaw was found in Samba. The security vulnerability occurs when KDC and the kpasswd service share a single account and set of keys, allowing them to decrypt each other's tickets. A user who has been requested to change their password, can exploit this flaw to obtain and use tickets to other services.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-2031

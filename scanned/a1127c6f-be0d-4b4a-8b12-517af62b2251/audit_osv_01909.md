# [H] ALPINE-CVE-2020-25719

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25719
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25719
Type: osv

## Affected
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.13.17-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.14.12-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.15.2-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.15.2-r0

## Details
A flaw was found in the way Samba, as an Active Directory Domain Controller, implemented Kerberos name-based authentication. The Samba AD DC, could become confused about the user a ticket represents if it did not strictly require a Kerberos PAC and always use the SIDs found within. The result could include total domain compromise.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25719

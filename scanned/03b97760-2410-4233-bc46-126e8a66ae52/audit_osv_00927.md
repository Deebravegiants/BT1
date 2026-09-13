# [M] ALPINE-CVE-2018-1140

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1140
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1140
Type: osv

## Affected
- Alpine:v3.10: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.11: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.12: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.13: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.14: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.15: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.16: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.17: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.18: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.19: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.20: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.21: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.7: `ldb` — affected >=0 <1.3.0-r1
- Alpine:v3.8: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.9: `ldb` — affected >=0 <1.3.5-r0
- Alpine:v3.10: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.11: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.12: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.13: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.14: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.15: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.16: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.17: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.18: `samba` — affected >=4.8.0 <4.8.4-r0
- Alpine:v3.19: `samba` — affected >=4.8.0 <4.8.4-r0

## Details
A missing input sanitization flaw was found in the implementation of LDP database used for the LDAP server. An attacker could use this flaw to cause a denial of service against a samba server, used as a Active Directory Domain Controller. All versions of Samba from 4.8.0 onwards are vulnerable

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1140

# [M] ALPINE-CVE-2019-14833

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14833
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14833
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.5.0 <4.10.10-r0
- Alpine:v3.11: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.12: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.13: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.14: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.15: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.16: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.17: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.18: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.19: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.20: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.21: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.22: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.23: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.24: `samba` — affected >=4.5.0 <4.11.2-r0
- Alpine:v3.8: `samba` — affected >=4.5.0 <4.8.12-r1
- Alpine:v3.9: `samba` — affected >=4.5.0 <4.8.12-r1

## Details
A flaw was found in Samba, all versions starting samba 4.5.0 before samba 4.9.15, samba 4.10.10, samba 4.11.2, in the way it handles a user password change or a new password for a samba user. The Samba Active Directory Domain Controller can be configured to use a custom script to check for password complexity. This configuration can fail to verify password complexity when non-ASCII characters are used in the password, which could lead to weak passwords being set for samba users, making it vulnerable to dictionary attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14833

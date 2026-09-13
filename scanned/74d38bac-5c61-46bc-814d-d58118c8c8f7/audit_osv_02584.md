# [M] ALPINE-CVE-2022-32746

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-32746
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32746
Type: osv

## Affected
- Alpine:v3.14: `samba` — affected >=4.3.0 <4.14.14-r0
- Alpine:v3.15: `samba` — affected >=4.3.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.3.0 <4.15.12-r0
- Alpine:v3.17: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.18: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.19: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.20: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.21: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.22: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.23: `samba` — affected >=4.3.0 <4.15.9-r0
- Alpine:v3.24: `samba` — affected >=4.3.0 <4.15.9-r0

## Details
A flaw was found in the Samba AD LDAP server. The AD DC database audit logging module can access LDAP message values freed by a preceding database module, resulting in a use-after-free issue. This issue is only possible when modifying certain privileged attributes, such as userAccountControl.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32746

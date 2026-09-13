# [M] ALPINE-CVE-2020-10730

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-10730
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10730
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.5.0 <4.10.17-r0
- Alpine:v3.11: `samba` — affected >=4.5.0 <4.11.14-r0
- Alpine:v3.12: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.13: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.14: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.15: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.16: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.17: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.18: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.19: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.20: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.21: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.22: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.23: `samba` — affected >=4.5.0 <4.12.5-r0
- Alpine:v3.24: `samba` — affected >=4.5.0 <4.12.5-r0

## Details
A NULL pointer dereference, or possible use-after-free flaw was found in Samba AD LDAP server in versions before 4.10.17, before 4.11.11 and before 4.12.4. Although some versions of Samba shipped with Red Hat Enterprise Linux do not support Samba in AD mode, the affected code is shipped with the libldb package. This flaw allows an authenticated user to possibly trigger a use-after-free or NULL pointer dereference. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10730

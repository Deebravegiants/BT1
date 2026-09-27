# [M] ALPINE-CVE-2020-10700

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-10700
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10700
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.10.0 <4.10.15-r0
- Alpine:v3.11: `samba` — affected >=4.10.0 <4.11.8-r0
- Alpine:v3.12: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.13: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.14: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.15: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.16: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.17: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.18: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.19: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.20: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.21: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.22: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.23: `samba` — affected >=4.10.0 <4.12.2-r0
- Alpine:v3.24: `samba` — affected >=4.10.0 <4.12.2-r0

## Details
A use-after-free flaw was found in the way samba AD DC LDAP servers, handled 'Paged Results' control is combined with the 'ASQ' control. A malicious user in a samba AD could use this flaw to cause denial of service. This issue affects all samba versions before 4.10.15, before 4.11.8 and before 4.12.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10700

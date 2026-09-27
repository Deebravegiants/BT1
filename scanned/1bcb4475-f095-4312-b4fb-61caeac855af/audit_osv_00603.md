# [H] ALPINE-CVE-2017-2619

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-2619
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2619
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.11: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.12: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.13: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.14: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.15: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.16: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.17: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.18: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.19: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.2: `samba` — affected >=4.5.0 <4.2.14-r2
- Alpine:v3.20: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.21: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.22: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.23: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.24: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.3: `samba` — affected >=4.5.0 <4.2.14-r2
- Alpine:v3.4: `samba` — affected >=4.5.0 <4.4.5-r3
- Alpine:v3.5: `samba` — affected >=4.5.0 <4.5.7-r0
- Alpine:v3.6: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.7: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.8: `samba` — affected >=4.5.0 <4.6.1-r0
- Alpine:v3.9: `samba` — affected >=4.5.0 <4.6.1-r0

## Details
Samba before versions 4.6.1, 4.5.7 and 4.4.11 are vulnerable to a malicious client using a symlink race to allow access to areas of the server file system not exported under the share definition.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2619

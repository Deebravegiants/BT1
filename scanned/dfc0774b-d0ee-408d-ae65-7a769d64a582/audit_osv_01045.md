# [M] ALPINE-CVE-2018-16853

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-16853
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16853
Type: osv

## Affected
- Alpine:v3.10: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.11: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.12: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.13: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.14: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.15: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.16: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.17: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.18: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.19: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.20: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.21: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.22: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.23: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.24: `samba` — affected >=4.7.0 <4.8.7-r0
- Alpine:v3.9: `samba` — affected >=4.7.0 <4.8.7-r0

## Details
Samba from version 4.7.0 has a vulnerability that allows a user in a Samba AD domain to crash the KDC when Samba is built in the non-default MIT Kerberos configuration. With this advisory the Samba Team clarify that the MIT Kerberos build of the Samba AD DC is considered experimental. Therefore the Samba Team will not issue security patches for this configuration. Additionally, Samba 4.7.12, 4.8.7 and 4.9.3 have been issued as security releases to prevent building of the AD DC with MIT Kerberos unless --with-experimental-mit-ad-dc is specified to the configure command.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16853

# [H] ALPINE-CVE-2018-16860

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16860
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16860
Type: osv

## Affected
- Alpine:v3.10: `heimdal` — affected >=0.8 <7.5.0-r4
- Alpine:v3.11: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.12: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.13: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.14: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.15: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.16: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.17: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.18: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.19: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.20: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.21: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.22: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.23: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.24: `heimdal` — affected >=0.8 <7.5.3-r4
- Alpine:v3.7: `heimdal` — affected >=0.8 <7.4.0-r3
- Alpine:v3.8: `heimdal` — affected >=0.8 <7.5.0-r2
- Alpine:v3.9: `heimdal` — affected >=0.8 <7.5.0-r3
- Alpine:v3.10: `samba` — affected >=4.8.0 <4.10.3-r0
- Alpine:v3.11: `samba` — affected >=4.8.0 <4.10.3-r0
- Alpine:v3.12: `samba` — affected >=4.8.0 <4.10.3-r0
- Alpine:v3.13: `samba` — affected >=4.8.0 <4.10.3-r0
- Alpine:v3.14: `samba` — affected >=4.8.0 <4.10.3-r0
- Alpine:v3.15: `samba` — affected >=4.8.0 <4.10.3-r0
- Alpine:v3.16: `samba` — affected >=4.8.0 <4.10.3-r0

## Details
A flaw was found in samba's Heimdal KDC implementation, versions 4.8.x up to, excluding 4.8.12, 4.9.x up to, excluding 4.9.8 and 4.10.x up to, excluding 4.10.3, when used in AD DC mode. A man in the middle attacker could use this flaw to intercept the request to the KDC and replace the user name (principal) in the request with any desired user name (principal) that exists in the KDC effectively obtaining a ticket for that principal.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16860

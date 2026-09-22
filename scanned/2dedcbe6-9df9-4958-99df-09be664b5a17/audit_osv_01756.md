# [M] ALPINE-CVE-2020-14318

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14318
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14318
Type: osv

## Affected
- Alpine:v3.11: `samba` — affected >=3.6.0 <4.11.16-r0
- Alpine:v3.12: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.13: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.14: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.15: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.16: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.17: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.18: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.19: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.20: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.21: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.22: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.23: `samba` — affected >=3.6.0 <4.12.9-r0
- Alpine:v3.24: `samba` — affected >=3.6.0 <4.12.9-r0

## Details
A flaw was found in the way samba handled file and directory permissions. An authenticated user could use this flaw to gain access to certain file and directory information which otherwise would be unavailable to the attacker.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14318

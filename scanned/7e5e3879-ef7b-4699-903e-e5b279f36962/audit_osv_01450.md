# [M] ALPINE-CVE-2019-14870

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14870
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14870
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.18: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.19: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.20: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.21: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.22: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.23: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.24: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.10: `samba` — affected >=4.0.0 <4.10.11-r0
- Alpine:v3.11: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.12: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.13: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.14: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.17: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.11.3-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.11.3-r0

## Details
All Samba versions 4.x.x before 4.9.17, 4.10.x before 4.10.11 and 4.11.x before 4.11.3 have an issue, where the S4U (MS-SFU) Kerberos delegation model includes a feature allowing for a subset of clients to be opted out of constrained delegation in any way, either S4U2Self or regular Kerberos authentication, by forcing all tickets for these clients to be non-forwardable. In AD this is implemented by a user attribute delegation_not_allowed (aka not-delegated), which translates to disallow-forwardable. However the Samba AD DC does not do that for S4U2Self and does set the forwardable flag even if the impersonated client has the not-delegated flag set.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14870

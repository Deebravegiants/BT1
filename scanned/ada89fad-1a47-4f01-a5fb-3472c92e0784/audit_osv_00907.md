# [M] ALPINE-CVE-2018-10916

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-10916
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10916
Type: osv

## Affected
- Alpine:v3.10: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.11: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.12: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.13: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.14: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.15: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.16: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.17: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.18: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.19: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.20: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.21: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.22: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.23: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.24: `lftp` — affected >=0 <4.8.4-r0
- Alpine:v3.9: `lftp` — affected >=0 <4.8.4-r0

## Details
It has been discovered that lftp up to and including version 4.8.3 does not properly sanitize remote file names, leading to a loss of integrity on the local system when reverse mirroring is used. A remote attacker may trick a user to use reverse mirroring on an attacker controlled FTP server, resulting in the removal of all files in the current working directory of the victim's system.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10916

# [C] ALPINE-CVE-2019-1353

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-1353
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1353
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=2.14.0 <2.22.2-r0
- Alpine:v3.11: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.12: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.13: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.14: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.15: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.16: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.17: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.18: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.19: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.20: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.21: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.22: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.23: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.24: `git` — affected >=2.14.0 <2.24.1-r0
- Alpine:v3.7: `git` — affected >=2.14.0 <2.15.4-r0
- Alpine:v3.8: `git` — affected >=2.14.0 <2.18.2-r0
- Alpine:v3.9: `git` — affected >=2.14.0 <2.20.2-r0
- Alpine:v3.11: `libgit2` — affected >=0 <0.28.4-r0

## Details
An issue was found in Git before v2.24.1, v2.23.1, v2.22.2, v2.21.1, v2.20.2, v2.19.3, v2.18.2, v2.17.3, v2.16.6, v2.15.4, and v2.14.6. When running Git in the Windows Subsystem for Linux (also known as "WSL") while accessing a working directory on a regular Windows drive, none of the NTFS protections were active.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1353

# [C] ALPINE-CVE-2018-17456

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-17456
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-17456
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.11: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.12: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.13: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.14: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.15: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.16: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.17: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.18: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.19: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.20: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.21: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.22: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.23: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.24: `git` — affected >=2.14.0 <2.19.1-r0
- Alpine:v3.5: `git` — affected >=2.14.0 <2.11.3-r2
- Alpine:v3.6: `git` — affected >=2.14.0 <2.13.7-r1
- Alpine:v3.7: `git` — affected >=2.14.0 <2.15.3-r0
- Alpine:v3.8: `git` — affected >=2.14.0 <2.18.1-r0
- Alpine:v3.9: `git` — affected >=2.14.0 <2.19.1-r0

## Details
Git before 2.14.5, 2.15.x before 2.15.3, 2.16.x before 2.16.5, 2.17.x before 2.17.2, 2.18.x before 2.18.1, and 2.19.x before 2.19.1 allows remote code execution during processing of a recursive "git clone" of a superproject if a .gitmodules file has a URL field beginning with a '-' character.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-17456

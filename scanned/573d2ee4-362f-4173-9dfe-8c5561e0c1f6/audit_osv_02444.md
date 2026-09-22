# [H] ALPINE-CVE-2022-24070

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24070
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24070
Type: osv

## Affected
- Alpine:v3.13: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.14: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.15: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.16: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.17: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.18: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.19: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.20: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.21: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.22: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.23: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.24: `subversion` — affected >=1.10.0 <1.14.2-r0

## Details
Subversion's mod_dav_svn is vulnerable to memory corruption. While looking up path-based authorization rules, mod_dav_svn servers may attempt to use memory which has already been freed. Affected Subversion mod_dav_svn servers 1.10.0 through 1.14.1 (inclusive). Servers that do not use mod_dav_svn are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24070

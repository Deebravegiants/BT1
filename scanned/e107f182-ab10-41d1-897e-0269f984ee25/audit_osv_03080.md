# [M] ALPINE-CVE-2024-39884

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-39884
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-39884
Type: osv

## Affected
- Alpine:v3.17: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.61-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.61-r0

## Details
A regression in the core of Apache HTTP Server 2.4.60 ignores some use of the legacy content-type based configuration of handlers.   "AddType" and similar configuration, under some circumstances where files are requested indirectly, result in source code disclosure of local content. For example, PHP scripts may be served instead of interpreted.

Users are recommended to upgrade to version 2.4.61, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-39884

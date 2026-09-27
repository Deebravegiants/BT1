# [M] ALPINE-CVE-2025-54090

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-54090
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-54090
Type: osv

## Affected
- Alpine:v3.19: `apache2` — affected >=0 <2.4.65-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.65-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.65-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.65-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.65-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.65-r0

## Details
A bug in Apache HTTP Server 2.4.64 results in all "RewriteCond expr ..." tests evaluating as "true".



Users are recommended to upgrade to version 2.4.65, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-54090

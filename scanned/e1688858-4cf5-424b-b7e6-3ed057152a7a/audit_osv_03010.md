# [M] ALPINE-CVE-2024-24795

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-24795
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-24795
Type: osv

## Affected
- Alpine:v3.16: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.59-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.59-r0

## Details
HTTP Response splitting in multiple modules in Apache HTTP Server allows an attacker that can inject malicious response headers into backend applications to cause an HTTP desynchronization attack.

Users are recommended to upgrade to version 2.4.59, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-24795

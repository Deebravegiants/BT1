# [M] ALPINE-CVE-2026-33007

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33007
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33007
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.67-r0

## Details
A NULL pointer dereference in the mod_authn_socache in Apache HTTP Server 2.4.66 and earlier allows an unauthenticated remote user to crash a child process in a caching forward proxy configuration.

Users are recommended to upgrade to version 2.4.67, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33007

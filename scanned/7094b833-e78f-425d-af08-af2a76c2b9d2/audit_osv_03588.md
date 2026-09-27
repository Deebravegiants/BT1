# [M] ALPINE-CVE-2026-33006

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-33006
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33006
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.67-r0

## Details
A timing attack against mod_auth_digest in Apache HTTP Server 2.4.66 allows a bypass of Digest authentication by a remote attacker.

Users are recommended to upgrade to version 2.4.67, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33006

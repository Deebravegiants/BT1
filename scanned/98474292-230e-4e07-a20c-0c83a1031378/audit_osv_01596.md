# [M] ALPINE-CVE-2019-3902

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-3902
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3902
Type: osv

## Affected
- Alpine:v3.10: `mercurial` — affected >=0 <4.9-r0
- Alpine:v3.11: `mercurial` — affected >=0 <4.9-r0
- Alpine:v3.12: `mercurial` — affected >=0 <4.9-r0
- Alpine:v3.13: `mercurial` — affected >=0 <4.9-r0
- Alpine:v3.7: `mercurial` — affected >=0 <4.5.2-r1
- Alpine:v3.8: `mercurial` — affected >=0 <4.6.1-r1
- Alpine:v3.9: `mercurial` — affected >=0 <4.9-r0

## Details
A flaw was found in Mercurial before 4.9. It was possible to use symlinks and subrepositories to defeat Mercurial's path-checking logic and write files outside a repository.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3902

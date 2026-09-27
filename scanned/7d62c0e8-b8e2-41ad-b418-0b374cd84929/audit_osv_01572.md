# [C] ALPINE-CVE-2019-3463

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-3463
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3463
Type: osv

## Affected
- Alpine:v3.13: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.14: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.15: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.16: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.17: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.18: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.19: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.20: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.21: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.22: `rssh` — affected >=0 <2.3.4-r2

## Details
Insufficient sanitization of arguments passed to rsync can bypass the restrictions imposed by rssh, a restricted shell that should restrict users to perform only rsync operations, resulting in the execution of arbitrary shell commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3463

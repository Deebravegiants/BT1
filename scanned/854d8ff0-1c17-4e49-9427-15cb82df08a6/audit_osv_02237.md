# [M] ALPINE-CVE-2021-3470

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3470
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3470
Type: osv

## Affected
- Alpine:v3.12: `redis` — affected >=6.0.0 <5.0.11-r0
- Alpine:v3.13: `redis` — affected >=6.0.0 <6.0.9-r0
- Alpine:v3.14: `redis` — affected >=6.0.0 <6.2.0-r0
- Alpine:v3.15: `redis` — affected >=6.0.0 <6.2.0-r0
- Alpine:v3.16: `redis` — affected >=6.0.0 <6.2.0-r0
- Alpine:v3.17: `redis` — affected >=6.0.0 <6.2.0-r0
- Alpine:v3.18: `redis` — affected >=6.0.0 <6.2.0-r0
- Alpine:v3.19: `redis` — affected >=6.0.0 <6.2.0-r0

## Details
A heap overflow issue was found in Redis in versions before 5.0.10, before 6.0.9 and before 6.2.0 when using a heap allocator other than jemalloc or glibc's malloc, leading to potential out of bound write or process crash. Effectively this flaw does not affect the vast majority of users, who use jemalloc or glibc malloc.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3470

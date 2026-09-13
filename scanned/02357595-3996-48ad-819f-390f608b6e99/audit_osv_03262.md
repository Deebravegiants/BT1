# [H] ALPINE-CVE-2025-32023

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-32023
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-32023
Type: osv

## Affected
- Alpine:v3.20: `valkey` — affected >=0 <7.2.11-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.11-r0
- Alpine:v3.22: `valkey` — affected >=0 <8.1.1-r2
- Alpine:v3.23: `valkey` — affected >=0 <8.1.1-r2
- Alpine:v3.24: `valkey` — affected >=0 <8.1.1-r2

## Details
Redis is an open source, in-memory database that persists on disk. From 2.8 to before 8.0.3, 7.4.5, 7.2.10, and 6.2.19, an authenticated user may use a specially crafted string to trigger a stack/heap out of bounds write on hyperloglog operations, potentially leading to remote code execution. The bug likely affects all Redis versions with hyperloglog operations implemented. This vulnerability is fixed in 8.0.3, 7.4.5, 7.2.10, and 6.2.19. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from executing hyperloglog operations. This can be done using ACL to restrict HLL commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-32023

# [C] ALPINE-CVE-2024-46981

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-46981
Ecosystem: Alpine:v3.15, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-46981
Type: osv

## Affected
- Alpine:v3.15: `redis` — affected >=6.2.0 <6.2.18-r0
- Alpine:v3.18: `redis` — affected >=6.2.0 <7.0.15-r2
- Alpine:v3.19: `redis` — affected >=6.2.0 <7.2.7-r0
- Alpine:v3.20: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.22: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.23: `valkey` — affected >=0 <7.2.8-r0
- Alpine:v3.24: `valkey` — affected >=0 <7.2.8-r0

## Details
Redis is an open source, in-memory database that persists on disk. An authenticated user may use a specially crafted Lua script to manipulate the garbage collector and potentially lead to remote code execution. The problem is fixed in 7.4.2, 7.2.7, and 6.2.17. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from executing Lua scripts. This can be done using ACL to restrict EVAL and EVALSHA commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-46981

# [H] ALPINE-CVE-2025-46819

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-46819
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46819
Type: osv

## Affected
- Alpine:v3.20: `valkey` — affected >=0 <7.2.11-r0
- Alpine:v3.21: `valkey` — affected >=0 <7.2.11-r0
- Alpine:v3.22: `valkey` — affected >=0 <8.1.4-r0
- Alpine:v3.23: `valkey` — affected >=0 <8.1.4-r0
- Alpine:v3.24: `valkey` — affected >=0 <8.1.4-r0

## Details
Redis is an open source, in-memory database that persists on disk. Versions 8.2.1 and below allow an authenticated user to use a specially crafted LUA script to read out-of-bound data or crash the server and subsequent denial of service. The problem exists in all versions of Redis with Lua scripting. This issue is fixed in version 8.2.2. To workaround this issue without patching the redis-server executable is to prevent users from executing Lua scripts. This can be done using ACL to block a script by restricting both the EVAL and FUNCTION command families.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46819

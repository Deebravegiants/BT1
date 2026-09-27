# [H] ALPINE-CVE-2022-24834

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-24834
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24834
Type: osv

## Affected
- Alpine:v3.16: `redis` — affected >=2.6.0 <7.0.12-r0
- Alpine:v3.17: `redis` — affected >=2.6.0 <7.0.12-r0
- Alpine:v3.18: `redis` — affected >=2.6.0 <7.0.12-r0
- Alpine:v3.19: `redis` — affected >=2.6.0 <7.0.12-r0

## Details
Redis is an in-memory database that persists on disk. A specially crafted Lua script executing in Redis can trigger a heap overflow in the cjson library, and result with heap corruption and potentially remote code execution. The problem exists in all versions of Redis with Lua scripting support, starting from 2.6, and affects only authenticated and authorized users. The problem is fixed in versions 7.0.12, 6.2.13, and 6.0.20.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24834

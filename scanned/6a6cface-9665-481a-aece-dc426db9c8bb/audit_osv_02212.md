# [M] ALPINE-CVE-2021-32672

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-32672
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-32672
Type: osv

## Affected
- Alpine:v3.11: `redis` — affected >=3.2.0 <5.0.14-r0
- Alpine:v3.12: `redis` — affected >=3.2.0 <5.0.14-r0
- Alpine:v3.13: `redis` — affected >=3.2.0 <6.0.16-r0
- Alpine:v3.14: `redis` — affected >=3.2.0 <6.2.6-r0
- Alpine:v3.15: `redis` — affected >=3.2.0 <6.2.6-r0
- Alpine:v3.16: `redis` — affected >=3.2.0 <6.2.6-r0
- Alpine:v3.17: `redis` — affected >=3.2.0 <6.2.6-r0
- Alpine:v3.18: `redis` — affected >=3.2.0 <6.2.6-r0
- Alpine:v3.19: `redis` — affected >=3.2.0 <6.2.6-r0

## Details
Redis is an open source, in-memory database that persists on disk. When using the Redis Lua Debugger, users can send malformed requests that cause the debugger’s protocol parser to read data beyond the actual buffer. This issue affects all versions of Redis with Lua debugging support (3.2 or newer). The problem is fixed in versions 6.2.6, 6.0.16 and 5.0.14.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-32672

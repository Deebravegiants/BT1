# [C] Redis Lua Use-After-Free may lead to remote code execution

## Summary
Severity: Critical
Advisory: BIT-keydb-2025-49844
Aliases: BIT-redis-2025-49844, BIT-valkey-2025-49844, CVE-2025-49844, GHSA-4789-qfc9-5f9q
Ecosystem: Bitnami
Published: 2025-10-16
Source: https://osv.dev/vulnerability/BIT-keydb-2025-49844
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.1.0 <8.2.2

## Details
Redis is an open source, in-memory database that persists on disk. Versions 8.2.1 and below allow an authenticated user to use a specially crafted Lua script to manipulate the garbage collector, trigger a use-after-free and potentially lead to remote code execution. The problem exists in all versions of Redis with Lua scripting. This issue is fixed in version 8.2.2. To workaround this issue without patching the redis-server executable is to prevent users from executing Lua scripts. This can be done using ACL to restrict EVAL and EVALSHA commands.

## References
- https://github.com/redis/redis/commit/d5728cb5795c966c5b5b1e0f0ac576a7e69af539
- https://github.com/redis/redis/releases/tag/8.2.2
- https://github.com/redis/redis/security/advisories/GHSA-4789-qfc9-5f9q
- https://nvd.nist.gov/vuln/detail/CVE-2025-49844
- http://www.openwall.com/lists/oss-security/2025/10/07/2
- https://github.com/lastvocher/redis-CVE-2025-49844

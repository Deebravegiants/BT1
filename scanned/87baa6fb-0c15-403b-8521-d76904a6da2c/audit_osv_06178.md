# [H] Redis: Authenticated users can execute LUA scripts as a different user

## Summary
Severity: High
Advisory: BIT-keydb-2025-46818
Aliases: BIT-redis-2025-46818, BIT-valkey-2025-46818, CVE-2025-46818, GHSA-qrv7-wcrx-q5jp
Ecosystem: Bitnami
Published: 2025-10-08
Source: https://osv.dev/vulnerability/BIT-keydb-2025-46818
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.1.0 <8.2.2

## Details
Redis is an open source, in-memory database that persists on disk. Versions 8.2.1 and below allow an authenticated user to use a specially crafted Lua script to manipulate different LUA objects and potentially run their own code in the context of another user. The problem exists in all versions of Redis with LUA scripting. This issue is fixed in version 8.2.2. A workaround to mitigate the problem without patching the redis-server executable is to prevent users from executing LUA scripts. This can be done using ACL to block a script by restricting both the EVAL and FUNCTION command families.

## References
- https://github.com/redis/redis/commit/45eac0262028c771b6f5307372814b75f49f7a9e
- https://github.com/redis/redis/releases/tag/8.2.2
- https://github.com/redis/redis/security/advisories/GHSA-qrv7-wcrx-q5jp
- https://nvd.nist.gov/vuln/detail/CVE-2025-46818

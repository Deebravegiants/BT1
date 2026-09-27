# [C] Redis' Lua library commands may lead to remote code execution

## Summary
Severity: Critical
Advisory: BIT-keydb-2024-46981
Aliases: BIT-redis-2024-46981, BIT-valkey-2024-46981, CVE-2024-46981, GHSA-39h2-x6c4-6w4c
Ecosystem: Bitnami
Published: 2025-01-08
Source: https://osv.dev/vulnerability/BIT-keydb-2024-46981
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.2.0 <6.3.4

## Details
Redis is an open source, in-memory database that persists on disk. An authenticated user may use a specially crafted Lua script to manipulate the garbage collector and potentially lead to remote code execution. The problem is fixed in 7.4.2, 7.2.7, and 6.2.17. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from executing Lua scripts. This can be done using ACL to restrict EVAL and EVALSHA commands.

## References
- https://github.com/redis/redis/releases/tag/6.2.17
- https://github.com/redis/redis/releases/tag/7.2.7
- https://github.com/redis/redis/releases/tag/7.4.2
- https://github.com/redis/redis/security/advisories/GHSA-39h2-x6c4-6w4c
- https://lists.debian.org/debian-lts-announce/2025/01/msg00018.html
- https://www.vicarius.io/vsociety/posts/cve-2024-46981-detect-redis-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2024-46981-mitigate-redis-vulnerability
- https://nvd.nist.gov/vuln/detail/CVE-2024-46981
- https://codeberg.org/redict/redict/releases/tag/7.3.2
- https://github.com/valkey-io/valkey/releases/tag/8.0.2
- https://redict.io/posts/2025-01-08-redict-7.3.2-released

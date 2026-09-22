# [H] Redis is vulnerable to DoS via specially crafted LUA scripts

## Summary
Severity: High
Advisory: BIT-keydb-2025-46819
Aliases: BIT-redis-2025-46819, BIT-valkey-2025-46819, CVE-2025-46819, GHSA-4c68-q8q8-3g4f
Ecosystem: Bitnami
Published: 2025-10-08
Source: https://osv.dev/vulnerability/BIT-keydb-2025-46819
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.1.0 <8.2.2

## Details
Redis is an open source, in-memory database that persists on disk. Versions 8.2.1 and below allow an authenticated user to use a specially crafted LUA script to read out-of-bound data or crash the server and subsequent denial of service. The problem exists in all versions of Redis with Lua scripting. This issue is fixed in version 8.2.2. To workaround this issue without patching the redis-server executable is to prevent users from executing Lua scripts. This can be done using ACL to block a script by restricting both the EVAL and FUNCTION command families.

## References
- https://github.com/redis/redis/commit/3a1624da2449ac3dbfc4bdaed43adf77a0b7bfba
- https://github.com/redis/redis/releases/tag/8.2.2
- https://github.com/redis/redis/security/advisories/GHSA-4c68-q8q8-3g4f
- https://nvd.nist.gov/vuln/detail/CVE-2025-46819
- https://www.vicarius.io/vsociety/posts/cve-2025-46819-detect-redis-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-46819-mitigate-redis-vulnerability

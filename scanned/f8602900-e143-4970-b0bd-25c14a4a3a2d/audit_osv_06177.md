# [H] Lua library commands may lead to integer overflow and potential RCE

## Summary
Severity: High
Advisory: BIT-keydb-2025-46817
Aliases: BIT-redis-2025-46817, BIT-valkey-2025-46817, CVE-2025-46817, GHSA-m8fj-85cg-7vhp
Ecosystem: Bitnami
Published: 2025-10-08
Source: https://osv.dev/vulnerability/BIT-keydb-2025-46817
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.1.0 <8.2.2

## Details
Redis is an open source, in-memory database that persists on disk. Versions 8.2.1 and below allow an authenticated user to use a specially crafted Lua script to cause an integer overflow and potentially lead to remote code execution The problem exists in all versions of Redis with Lua scripting. This issue is fixed in version 8.2.2.

## References
- https://github.com/redis/redis/commit/fc9abc775e308374f667fdf3e723ef4b7eb0e3ca
- https://github.com/redis/redis/releases/tag/8.2.2
- https://github.com/redis/redis/security/advisories/GHSA-m8fj-85cg-7vhp
- https://nvd.nist.gov/vuln/detail/CVE-2025-46817

# [C] redis-check-aof may lead to stack overflow and potential RCE

## Summary
Severity: Critical
Advisory: BIT-keydb-2025-27151
Aliases: BIT-redis-2025-27151, BIT-valkey-2025-27151, CVE-2025-27151, GHSA-5453-q98w-cmvm
Ecosystem: Bitnami
Published: 2025-05-31
Source: https://osv.dev/vulnerability/BIT-keydb-2025-27151
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0

## Details
Redis is an open source, in-memory database that persists on disk. In versions starting from 7.0.0 to before 8.0.2, a stack-based buffer overflow exists in redis-check-aof due to the use of memcpy with strlen(filepath) when copying a user-supplied file path into a fixed-size stack buffer. This allows an attacker to overflow the stack and potentially achieve code execution. This issue has been patched in version 8.0.2.

## References
- https://github.com/redis/redis/commit/643b5db235cb82508e72f11c7b4bbfc7dc39be56
- https://github.com/redis/redis/releases/tag/8.0.2
- https://github.com/redis/redis/security/advisories/GHSA-5453-q98w-cmvm
- https://nvd.nist.gov/vuln/detail/CVE-2025-27151

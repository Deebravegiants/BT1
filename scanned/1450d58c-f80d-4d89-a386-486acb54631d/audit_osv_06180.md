# [H] Redis DoS Vulnerability due to bad connection error handling

## Summary
Severity: High
Advisory: BIT-keydb-2025-48367
Aliases: BIT-redis-2025-48367, BIT-valkey-2025-48367, CVE-2025-48367, GHSA-4q32-c38c-pwgq
Ecosystem: Bitnami
Published: 2025-10-16
Source: https://osv.dev/vulnerability/BIT-keydb-2025-48367
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.4.0 <7.4.5

## Details
Redis is an open source, in-memory database that persists on disk. An unauthenticated connection can cause repeated IP protocol errors, leading to client starvation and, ultimately, a denial of service. This vulnerability is fixed in 8.0.3, 7.4.5, 7.2.10, and 6.2.19.

## References
- https://github.com/redis/redis/commit/bde62951accfc4bb0a516276fd0b4b307e140ce2
- https://github.com/redis/redis/releases/tag/6.2.19
- https://github.com/redis/redis/releases/tag/7.2.10
- https://github.com/redis/redis/releases/tag/7.4.5
- https://github.com/redis/redis/releases/tag/8.0.3
- https://github.com/redis/redis/security/advisories/GHSA-4q32-c38c-pwgq
- https://nvd.nist.gov/vuln/detail/CVE-2025-48367

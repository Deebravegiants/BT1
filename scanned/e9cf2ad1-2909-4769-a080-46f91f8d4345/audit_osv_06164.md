# [M] Redis string pattern matching can be abused to achieve Denial of Service

## Summary
Severity: Medium
Advisory: BIT-keydb-2022-36021
Aliases: BIT-redis-2022-36021, BIT-valkey-2022-36021, CVE-2022-36021, GHSA-jr7j-rfj5-8xqv
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2022-36021
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.9

## Details
Redis is an in-memory database that persists on disk. Authenticated users can use string matching commands (like `SCAN` or `KEYS`) with a specially crafted pattern to trigger a denial-of-service attack on Redis, causing it to hang and consume 100% CPU time. The problem is fixed in Redis versions 6.0.18, 6.2.11, 7.0.9.

## References
- https://github.com/redis/redis/commit/dcbfcb916ca1a269b3feef86ee86835294758f84
- https://github.com/redis/redis/security/advisories/GHSA-jr7j-rfj5-8xqv
- https://nvd.nist.gov/vuln/detail/CVE-2022-36021

# [H] Potential heap overflow in Redis

## Summary
Severity: High
Advisory: BIT-keydb-2022-31144
Aliases: BIT-redis-2022-31144, BIT-valkey-2022-31144, CVE-2022-31144, GHSA-96f7-42fg-2jrh
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2022-31144
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.4

## Details
Redis is an in-memory database that persists on disk. A specially crafted `XAUTOCLAIM` command on a stream key in a specific state may result with heap overflow, and potentially remote code execution. This problem affects versions on the 7.x branch prior to 7.0.4. The patch is released in version 7.0.4.

## References
- https://github.com/redis/redis/releases/tag/7.0.4
- https://github.com/redis/redis/security/advisories/GHSA-96f7-42fg-2jrh
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20220909-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2022-31144

# [M] BIT-keydb-2021-31294

## Summary
Severity: Medium
Advisory: BIT-keydb-2021-31294
Aliases: BIT-redis-2021-31294, BIT-valkey-2021-31294, CVE-2021-31294
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2021-31294
Type: osv

## Affected
- Bitnami: `keydb` — affected >=0 <6.2.0

## Details
Redis before 6cbea7d allows a replica to cause an assertion failure in a primary server by sending a non-administrative command (specifically, a SET command). NOTE: this was fixed for Redis 6.2.x and 7.x in 2021. Versions before 6.2 were not intended to have safety guarantees related to this.

## References
- https://github.com/redis/redis/commit/46f4ebbe842620f0976a36741a72482620aa4b48
- https://github.com/redis/redis/commit/6cbea7d29b5285692843bc1c351abba1a7ef326f
- https://github.com/redis/redis/issues/8712
- https://security.netapp.com/advisory/ntap-20230814-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2021-31294

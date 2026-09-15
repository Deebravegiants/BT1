# [H] Integer overflow that can lead to heap overflow in redis-cli, redis-sentinel on some platforms

## Summary
Severity: High
Advisory: BIT-keydb-2021-32762
Aliases: BIT-redis-2021-32762, BIT-valkey-2021-32762, CVE-2021-32762, GHSA-833w-8v3m-8wwr
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2021-32762
Type: osv

## Affected
- Bitnami: `keydb` — affected >=6.2.0 <6.2.6

## Details
Redis is an open source, in-memory database that persists on disk. The redis-cli command line tool and redis-sentinel service may be vulnerable to integer overflow when parsing specially crafted large multi-bulk network replies. This is a result of a vulnerability in the underlying hiredis library which does not perform an overflow check before calling the calloc() heap allocation function. This issue only impacts systems with heap allocators that do not perform their own overflow checks. Most modern systems do and are therefore not likely to be affected. Furthermore, by default redis-sentinel uses the jemalloc allocator which is also not vulnerable. The problem is fixed in Redis versions 6.2.6, 6.0.16 and 5.0.14.

## References
- https://github.com/redis/redis/commit/0215324a66af949be39b34be2d55143232c1cb71
- https://github.com/redis/redis/security/advisories/GHSA-833w-8v3m-8wwr
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HTYQ5ZF37HNGTZWVNJD3VXP7I6MEEF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VL5KXFN3ATM7IIM7Q4O4PWTSRGZ5744Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WR5WKJWXD4D6S3DJCZ56V74ESLTDQRAB/
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20211104-0003/
- https://www.debian.org/security/2021/dsa-5001
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-32762

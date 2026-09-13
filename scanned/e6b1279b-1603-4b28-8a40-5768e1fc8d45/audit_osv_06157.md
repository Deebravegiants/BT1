# [H] Integer overflow issue with strings in Redis

## Summary
Severity: High
Advisory: BIT-keydb-2021-41099
Aliases: BIT-redis-2021-41099, BIT-valkey-2021-41099, CVE-2021-41099, GHSA-j3cr-9h5g-6cph
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2021-41099
Type: osv

## Affected
- Bitnami: `keydb` — affected >=6.2.0 <6.2.6

## Details
Redis is an open source, in-memory database that persists on disk. An integer overflow bug in the underlying string library can be used to corrupt the heap and potentially result with denial of service or remote code execution. The vulnerability involves changing the default proto-max-bulk-len configuration parameter to a very large value and constructing specially crafted network payloads or commands. The problem is fixed in Redis versions 6.2.6, 6.0.16 and 5.0.14. An additional workaround to mitigate the problem without patching the redis-server executable is to prevent users from modifying the proto-max-bulk-len configuration parameter. This can be done using ACL to restrict unprivileged users from using the CONFIG SET command.

## References
- https://github.com/redis/redis/commit/c6ad876774f3cc11e32681ea02a2eead00f2c521
- https://github.com/redis/redis/security/advisories/GHSA-j3cr-9h5g-6cph
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HTYQ5ZF37HNGTZWVNJD3VXP7I6MEEF42/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VL5KXFN3ATM7IIM7Q4O4PWTSRGZ5744Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WR5WKJWXD4D6S3DJCZ56V74ESLTDQRAB/
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20211104-0003/
- https://www.debian.org/security/2021/dsa-5001
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-41099

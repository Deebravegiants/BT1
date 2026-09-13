# [C] BIT-redis-2022-0543

## Summary
Severity: Critical
Advisory: BIT-redis-2022-0543
Aliases: CVE-2022-0543
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redis-2022-0543
Type: osv

## Affected
- Bitnami: `redis` — affected unspecified

## Details
It was discovered, that redis, a persistent key-value database, due to a packaging issue, is prone to a (Debian-specific) Lua sandbox escape, which could result in remote code execution.

## References
- http://packetstormsecurity.com/files/166885/Redis-Lua-Sandbox-Escape.html
- https://bugs.debian.org/1005787
- https://lists.debian.org/debian-security-announce/2022/msg00048.html
- https://security.netapp.com/advisory/ntap-20220331-0004/
- https://www.debian.org/security/2022/dsa-5081
- https://www.ubercomp.com/posts/2022-01-20_redis_on_debian_rce

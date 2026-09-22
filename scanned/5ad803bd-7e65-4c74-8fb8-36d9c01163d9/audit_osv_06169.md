# [H] Redis vulnerable to integer overflow in certain payloads

## Summary
Severity: High
Advisory: BIT-keydb-2023-41056
Aliases: BIT-redis-2023-41056, BIT-valkey-2023-41056, CVE-2023-41056, GHSA-xr47-pcmx-fq2m
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2023-41056
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.2.0 <7.2.4

## Details
Redis is an in-memory database that persists on disk. Redis incorrectly handles resizing of memory buffers which can result in integer overflow that leads to heap overflow and potential remote code execution. This issue has been patched in version 7.0.15 and 7.2.4.

## References
- https://github.com/redis/redis/releases/tag/7.0.15
- https://github.com/redis/redis/releases/tag/7.2.4
- https://github.com/redis/redis/security/advisories/GHSA-xr47-pcmx-fq2m
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3JTGQJ2YLYB24B72I5B5H32YIMPVSWIT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JTWHPLC3RI67VNRDOIXLDVNC5YMYBMQN/
- https://security.netapp.com/advisory/ntap-20240223-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2023-41056

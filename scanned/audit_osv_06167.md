# [M] `HINCRBYFLOAT` can be used to crash a redis-server process

## Summary
Severity: Medium
Advisory: BIT-keydb-2023-28856
Aliases: BIT-redis-2023-28856, BIT-valkey-2023-28856, CVE-2023-28856, GHSA-hjv8-vjf6-wcr6
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2023-28856
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.11

## Details
Redis is an open source, in-memory database that persists on disk. Authenticated users can use the `HINCRBYFLOAT` command to create an invalid hash field that will crash Redis on access in affected versions. This issue has been addressed in in versions 7.0.11, 6.2.12, and 6.0.19. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/redis/redis/commit/bc7fe41e5857a0854d524e2a63a028e9394d2a5c
- https://github.com/redis/redis/pull/11149
- https://github.com/redis/redis/security/advisories/GHSA-hjv8-vjf6-wcr6
- https://lists.debian.org/debian-lts-announce/2023/04/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EQ4DJSO4DMR55AWK6OPVJH5UTEB35R2Z/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LPUTH7NBQTZDVJWFNUD24ZCS6NDUFYS6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OQGKMKSQE67L32HE6W5EI2I2YKW5VWHI/
- https://security.netapp.com/advisory/ntap-20230601-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2023-28856

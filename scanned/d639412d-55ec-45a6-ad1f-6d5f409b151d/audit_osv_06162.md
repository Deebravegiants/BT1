# [C] Redis subject to Integer Overflow leading to Remote Code Execution via Heap Overflow

## Summary
Severity: Critical
Advisory: BIT-keydb-2022-35951
Aliases: BIT-redis-2022-35951, BIT-valkey-2022-35951, CVE-2022-35951, GHSA-5gc4-76rx-22c9
Ecosystem: Bitnami
Published: 2024-08-22
Source: https://osv.dev/vulnerability/BIT-keydb-2022-35951
Type: osv

## Affected
- Bitnami: `keydb` — affected >=7.0.0 <7.0.5

## Details
Redis is an in-memory database that persists on disk. Versions 7.0.0 and above, prior to 7.0.5 are vulnerable to an Integer Overflow. Executing an `XAUTOCLAIM` command on a stream key in a specific state, with a specially crafted `COUNT` argument may cause an integer overflow, a subsequent heap overflow, and potentially lead to remote code execution. This has been patched in Redis version 7.0.5. No known workarounds exist.

## References
- https://github.com/redis/redis/security/advisories/GHSA-5gc4-76rx-22c9
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A7INCOOFPPEAKNDBZU3TIZJPYXBULI2C/
- https://security.gentoo.org/glsa/202209-17
- https://security.netapp.com/advisory/ntap-20221020-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-35951

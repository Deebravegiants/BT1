# [H] Redis: Bug in XACKDEL may lead to stack overflow and potential RCE

## Summary
Severity: High
Advisory: BIT-keydb-2025-62507
Aliases: BIT-redis-2025-62507, CVE-2025-62507, GHSA-jhjx-x4cf-4vm8
Ecosystem: Bitnami
Published: 2025-11-07
Source: https://osv.dev/vulnerability/BIT-keydb-2025-62507
Type: osv

## Affected
- Bitnami: `keydb` — affected >=8.2.0 <8.2.3

## Details
Redis is an open source, in-memory database that persists on disk. In versions 8.2.0 and above, a user can run the XACKDEL command with multiple ID's and trigger a stack buffer overflow, which may potentially lead to remote code execution. This issue is fixed in version 8.2.3. To workaround this issue without patching the redis-server executable is to prevent users from executing XACKDEL operation. This can be done using ACL to restrict XACKDEL command.

## References
- https://github.com/redis/redis/commit/5f83972188f6e5b1d6f1940218c650a9cbdf7741
- https://github.com/redis/redis/releases/tag/8.2.3
- https://github.com/redis/redis/security/advisories/GHSA-jhjx-x4cf-4vm8
- https://nvd.nist.gov/vuln/detail/CVE-2025-62507

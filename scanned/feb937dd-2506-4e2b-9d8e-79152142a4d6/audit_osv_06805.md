# [M] BIT-memcached-2021-37519

## Summary
Severity: Medium
Advisory: BIT-memcached-2021-37519
Aliases: CVE-2021-37519
Ecosystem: Bitnami
Published: 2024-11-08
Source: https://osv.dev/vulnerability/BIT-memcached-2021-37519
Type: osv

## Affected
- Bitnami: `memcached` — affected >=0 <1.6.10

## Details
Buffer Overflow vulnerability in authfile.c memcached 1.6.9 allows attackers to cause a denial of service via crafted authenticattion file.

## References
- https://github.com/memcached/memcached/issues/805
- https://github.com/memcached/memcached/pull/806/commits/264722ae4e248b453be00e97197dadc685b60fd0
- https://nvd.nist.gov/vuln/detail/CVE-2021-37519
- https://github.com/memcached/memcached/commit/ddee3e27a031be22f5f28c160be18fd3cb9bc63d

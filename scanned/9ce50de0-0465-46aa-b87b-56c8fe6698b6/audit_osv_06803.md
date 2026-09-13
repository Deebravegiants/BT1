# [H] BIT-memcached-2020-10931

## Summary
Severity: High
Advisory: BIT-memcached-2020-10931
Aliases: CVE-2020-10931
Ecosystem: Bitnami
Published: 2024-11-08
Source: https://osv.dev/vulnerability/BIT-memcached-2020-10931
Type: osv

## Affected
- Bitnami: `memcached` — affected >=1.6.0 <1.6.2

## Details
Memcached 1.6.x before 1.6.2 allows remote attackers to cause a denial of service (daemon crash) via a crafted binary protocol header to try_read_command_binary in memcached.c.

## References
- https://github.com/memcached/memcached/commit/02c6a2b62ddcb6fa4569a591d3461a156a636305
- https://github.com/memcached/memcached/issues/629
- https://github.com/memcached/memcached/wiki/ReleaseNotes162
- https://nvd.nist.gov/vuln/detail/CVE-2020-10931

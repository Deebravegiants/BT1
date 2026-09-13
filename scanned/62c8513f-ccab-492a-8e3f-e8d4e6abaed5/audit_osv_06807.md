# [C] BIT-memcached-2023-46853

## Summary
Severity: Critical
Advisory: BIT-memcached-2023-46853
Aliases: CVE-2023-46853
Ecosystem: Bitnami
Published: 2024-11-08
Source: https://osv.dev/vulnerability/BIT-memcached-2023-46853
Type: osv

## Affected
- Bitnami: `memcached` — affected >=0 <1.6.22

## Details
In Memcached before 1.6.22, an off-by-one error exists when processing proxy requests in proxy mode, if \n is used instead of \r\n.

## References
- https://github.com/memcached/memcached/commit/6987918e9a3094ec4fc8976f01f769f624d790fa
- https://github.com/memcached/memcached/compare/1.6.21...1.6.22
- https://nvd.nist.gov/vuln/detail/CVE-2023-46853

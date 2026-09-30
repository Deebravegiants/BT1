# [H] BIT-memcached-2023-46852

## Summary
Severity: High
Advisory: BIT-memcached-2023-46852
Aliases: CVE-2023-46852
Ecosystem: Bitnami
Published: 2024-11-08
Source: https://osv.dev/vulnerability/BIT-memcached-2023-46852
Type: osv

## Affected
- Bitnami: `memcached` — affected >=0 <1.6.22

## Details
In Memcached before 1.6.22, a buffer overflow exists when processing multiget requests in proxy mode, if there are many spaces after the "get" substring.

## References
- https://github.com/memcached/memcached/commit/76a6c363c18cfe7b6a1524ae64202ac9db330767
- https://github.com/memcached/memcached/compare/1.6.21...1.6.22
- https://nvd.nist.gov/vuln/detail/CVE-2023-46852

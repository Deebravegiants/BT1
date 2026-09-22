# [H] BIT-memcached-2026-47784

## Summary
Severity: High
Advisory: BIT-memcached-2026-47784
Aliases: CVE-2026-47784
Ecosystem: Bitnami
Published: 2026-05-22
Source: https://osv.dev/vulnerability/BIT-memcached-2026-47784
Type: osv

## Affected
- Bitnami: `memcached` — affected >=0 <1.6.42

## Details
In memcached before 1.6.42, password data for SASL password database authentication has a timing side channel because memcmp is used by sasl_server_userdb_checkpass.

## References
- https://github.com/memcached/memcached/commit/d13f282b4bce33a9c33b8a1bbf07f12114160fed
- https://github.com/memcached/memcached/compare/1.6.41...1.6.42
- https://github.com/memcached/memcached/wiki/ReleaseNotes1642
- https://nvd.nist.gov/vuln/detail/CVE-2026-47784

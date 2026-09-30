# [H] PgBouncer crash in kill_pool_logins_server_error

## Summary
Severity: High
Advisory: BIT-pgbouncer-2026-6666
Aliases: CVE-2026-6666
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2026-6666
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.25.2

## Details
A possible null pointer reference in PgBouncer before 1.25.2 could lead to a crash, if a server sends an error response without SQLSTATE field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6666
- https://www.pgbouncer.org/changelog.html#pgbouncer-125x

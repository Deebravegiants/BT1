# [C] PgBouncer default auth_query does not take Postgres password expiry into account

## Summary
Severity: Critical
Advisory: BIT-pgbouncer-2025-2291
Aliases: CVE-2025-2291
Ecosystem: Bitnami
Published: 2025-04-18
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2025-2291
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.24.1

## Details
Password can be used past expiry in PgBouncer due to auth_query not taking into account Postgres its VALID UNTIL value, which allows an attacker to log in with an already expired password

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2291
- https://www.pgbouncer.org/changelog.html#pgbouncer-124x
- https://lists.debian.org/debian-lts-announce/2025/05/msg00032.html

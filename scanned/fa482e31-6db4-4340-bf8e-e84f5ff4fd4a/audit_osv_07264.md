# [M] PgBouncer missing authorization check in KILL_CLIENT admin command

## Summary
Severity: Medium
Advisory: BIT-pgbouncer-2026-6667
Aliases: CVE-2026-6667
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2026-6667
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.25.2

## Details
PgBouncer before 1.25.2 did not perform an appropriate authorization check for the KILL_CLIENT admin command. All users with access to the administration console (which itself requires authorization) could run this command. It would have been correct to allow only users listed in the admin_users parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6667
- https://www.pgbouncer.org/changelog.html#pgbouncer-125x

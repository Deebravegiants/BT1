# [H] PgBouncer integer overflow in PgBouncer network packet parsing

## Summary
Severity: High
Advisory: BIT-pgbouncer-2026-6664
Aliases: CVE-2026-6664
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2026-6664
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.25.2

## Details
An integer overflow in network packet parsing code in PgBouncer before 1.25.2 bypasses a boundary check and can lead to a crash. An unauthenticated remote attacker can crash PgBouncer with a malformed SCRAM authentication packet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6664
- https://www.pgbouncer.org/changelog.html#pgbouncer-125x

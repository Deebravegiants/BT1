# [C] PgBouncer buffer overflow in SCRAM

## Summary
Severity: Critical
Advisory: BIT-pgbouncer-2026-6665
Aliases: CVE-2026-6665
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2026-6665
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.25.2

## Details
The SCRAM code in PgBouncer before 1.25.2 did not check the return value of strlcat() correctly when building the contents of the SCRAM client-final-message. A malicious backend that sends a SCRAM server-final-message with a long nonce can trigger a stack overflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6665
- https://www.pgbouncer.org/changelog.html#pgbouncer-125x
